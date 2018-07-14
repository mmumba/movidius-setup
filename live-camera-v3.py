#!/usr/bin/python3
# we should try this tips from https://ncsforum.movidius.com/discussion/861/using-the-pi-camera-not-usb-camera-some-sample-code
# if this doesnt work
# MMM - updated modification
import os
import cv2
import sys
import numpy
import ntpath
import argparse

from mvnc import mvncapi
ARGS                 = None  # Variable to store commandline arguments
camera               = None  # OpenCV object for video capture
graph                = None  # Variable to store neural network graph
# input_fifo           = None  # Variable to store input fifo
# output_fifo          = None  # Variable to store output fifo
# device               = None  #  Device

# ---- STEP 1: Open the enumerated device and get a handle to it -------------
def open_ncs_device(): 
    # MM - Updated entire function to align with NCSDK API V2 (https://movidius.github.io/ncsdk/ncapi/ncapi2/py_api/readme.html)
    device_list = mvncapi.enumerate_devices()   # Get a list of available device identifiers
    if len( device_list ) == 0:
        print( "No devices found" )
        quit()     
    device = mvncapi.Device(device_list[0]) # Get a handle to the first enumerated device and open it
    device.open()

    return device

# ---- STEP 2: Load a graph file onto the NCS device -------------------------

def load_graph( device ):

    # Read the graph file into a buffer
    with open( ARGS.graph, mode='rb' ) as f:
        graph_buffer = f.read()

    # Load the graph buffer into the NCS
    graph =  mvncapi.Graph( ARGS.graph )
    
    # Set up fifos
    input_fifo, output_fifo = graph.allocate_with_fifos(device, graph_buffer)
    #check opbject exists
    # print("from load_graph(), input_fifo contents %s ", str(input_fifo))  
        


    # Allocate the Graph and create and allocate two associate Fifos for input and output
    # input_fifo, output_fifo = graph.allocate_with_fifos(device, graph_buffer)

    return graph, input_fifo, output_fifo

# ---- STEP 3: Pre-process the images ----------------------------------------

def pre_process_image( frame ):

    # Resize image [Image size is defined by choosen network, during training]
    img = cv2.resize( frame, tuple( ARGS.dim ) )

    # Extract/crop a section of the frame and resize it
    height, width, channels = frame.shape
    x1 = int( width / 3 )
    y1 = int( height / 4 )
    x2 = int( width * 2 / 3 )
    y2 = int( height * 3 / 4 )

    cv2.rectangle( frame, ( x1, y1 ) , ( x2, y2 ), ( 0, 255, 0 ), 2 )
    img = frame[ y1 : y2, x1 : x2 ]

    # Resize image [Image size if defined by choosen network, during training]
    img = cv2.resize( img, tuple( ARGS.dim ) )

    # Convert BGR to RGB [OpenCV reads image in BGR, some networks may need RGB]
    if( ARGS.colormode == "rgb" ):
        img = img[:, :, ::-1]

    # Mean subtraction & scaling [A common technique used to center the data]
    img = img.astype( numpy.float16 )
    img = ( img - numpy.float16( ARGS.mean ) ) * ARGS.scale

    return img

# ---- STEP 4: Read & print inference results from the NCS -------------------

def infer_image( graph, frame, input_fifo, output_fifo ):
    
    input_tensor = pre_process_image( frame )
    
    # Write an input tensor to the input Fifo and queue an inference
    #  graph.queue_inference_with_fifo_elem(input_fifo, output_fifo, input_tensor, None, 'tensor1')
    # graph.queue_inference_with_fifo_elem(input_fifo, output_fifo, input_tensor, None)

    #check object input_fifo exists  
    print("contents of input_fifo  %s", str(input_fifo))

    graph.queue_inference_with_fifo_elem(input_fifo, output_fifo, input_tensor.astype(numpy.float32), 'tensor1')
    
     # Read the inference result tensor from the output Fifo
    result_tensor, user_obj = output_fifo.read_elem()
    
    # Find the index of highest confidence 
    top_prediction = result_tensor.argmax()

    # Get execution time
    # inference_time =  graph.GetGraphOption(mvncapi.GraphOption.TIME_TAKEN ) #MM
    inference_time = graph.get_option(mvncapi.GraphOption.RO_TIME_TAKEN)

    print(  "I am %3.1f%%" % (100.0 * result_tensor[top_prediction] ) + " confident" + " you are " + labels[top_prediction] + " ( %.2f ms )" % ( numpy.sum( inference_time ) ) )

    # If a display is available, show the image on which inference was performed
    if 'DISPLAY' in os.environ:
        cv2.imshow( 'NCS live inference', frame )

# ---- STEP 5: Unload the graph and close the device -------------------------

def close_ncs_device( device, graph,input_fifo,output_fifo ):
    
    # Destroy the Fifos
    input_fifo.destroy()
    output_fifo.destroy()

    graph.destroy()
    device.close()
    device.destroy()
    # graph.DeallocateGraph()  # MM -replaced with above from 
    # device.CloseDevice()     # MM -replaced with above from 
    camera.release()
    cv2.destroyAllWindows()

# ---- Main function (entry point for this script ) --------------------------

def main():

    device = open_ncs_device()
    graph, input_fifo, output_fifo = load_graph( device )

    # check object exists 
    # print("input_fifo object in main ... contents %s ", str(input_fifo))

    # Main loop: Capture live stream & send frames to NCS & run inference
    while( True ):
        ret, frame = camera.read()
        infer_image( graph, frame, input_fifo, output_fifo )
       

        # Display the frame for 5ms, and close the window so that the next
        # frame can be displayed. Close the window if 'q' or 'Q' is pressed.
        if( cv2.waitKey( 5 ) & 0xFF == ord( 'q' ) ):
            break

    close_ncs_device( device, graph,input_fifo,output_fifo )

# ---- Define 'main' function as the entry point for this script -------------

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Image classifier using Intel Movidius Neural Compute Stick." )
    
    # changed path to neural network graph for inceptionV3
    parser.add_argument( '-g', '--graph', type=str,default='./graph',help="Absolute path to the neural network graph file." )

    parser.add_argument( '-v', '--video', type=int, default=0, help="Index of your computer's video device. ex. 0 for /dev/video0" )
    
    # changed path and filename with labels
    parser.add_argument( '-l', '--labels', type=str,default='./categories.txt',help="Absolute path to labels file." )

    # changed (a) from float to int (b) changed to  mean [128,128,128]
    parser.add_argument( '-M', '--mean', type=int,nargs='+',default=[128, 128, 128],help="',' delimited floating point values for image mean." )

    parser.add_argument( '-S', '--scale', type=float, default=1, help="Absolute path to labels file." )
    
    # changed dimensions to 299 x 299 to match inceptionV3
    parser.add_argument( '-D', '--dim', type=int, nargs='+', default=[299, 299],help="Image dimensions. ex. -D 224 224" )
    
    # changed dimensions to 229 x 229 to match inceptionV3
    parser.add_argument( '-c', '--colormode', type=str, default="rgb",help="RGB vs BGR color sequence. This is network dependent." )

    ARGS = parser.parse_args()

    # Create a VideoCapture object
    camera = cv2.VideoCapture( ARGS.video )

    # Set camera resolution
    camera.set( cv2.CAP_PROP_FRAME_WIDTH, 620 )
    camera.set( cv2.CAP_PROP_FRAME_HEIGHT, 480 )

    # Load the labels file
    labels =[ line.rstrip('\n') for line in
              open( ARGS.labels ) if line != 'classes\n']

    main()

# ==== End of file ===========================================================
