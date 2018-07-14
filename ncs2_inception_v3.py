#! /usr/bin/python3
# *-* coding: utf-8 *-*

from mvnc import mvncapi as mvnc
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import cv2

PREPROCESSED_DIMS = (299, 299)

def preprocess_img(image):
    preprocessed = cv2.resize(image, PREPROCESSED_DIMS)
    return preprocessed


def predict(image, graph):
    input_image = preprocess_img(image)
    graph.LoadTensor(input_image, None)
    output, obj = graph.GetResult()
    print("WTF 0: " + str(output))
    print("WTF 1: " + str(obj))
    return output


if __name__ == "__main__":
    # execute only if run as a script

    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-g", "--graph", required=True,
                   help="path to input graph file")
    ap.add_argument("-c", "--confidence", default=.5,
                   help="confidence threshold")
    ap.add_argument("-d", "--display", type=int, default=0,
                    help="switch to display image on screen")
    args = vars(ap.parse_args())

    # grab a list of all NCS devices plugged in to USB
    print("[INFO] finding NCS devices...")
    devices = mvnc.enumerate_devices()
    # if no devices found, exit the script
    if len(devices) == 0:
        print("[INFO] No devices found. Please plug in a NCS")
        quit()

    # use the first device since this is a simple test script
    # (you'll want to modify this is using multiple NCS devices)
    print("[INFO] found {} devices. device0 will be used. "
          "opening device0...".format(len(devices)))
    device = mvnc.Device(devices[0])
    device.open()

    # open the CNN graph file
    print("[INFO] loading the graph file into RPi memory...")
    with open("./" + str(args["graph"]), mode="rb") as f:
        graph_in_memory = f.read()

    graph = mvnc.Graph('graph1')
    # Initialize a graph object
    # load the graph into the NCS
    # Allocate the graph to the device and create input and output Fifos with default arguments
    print("[INFO] allocating the graph on the NCS...")
    inputs, outputs = graph.allocate_with_fifos(device=device,
            graph_buffer=graph_in_memory)

    # open a pointer to the video stream thread and allow the buffer to
    # start to fill, then start the FPS counter
    print("[INFO] starting the video stream and FPS counter...")
    vs = VideoStream().start()   # usePiCamera=True
    fps = FPS().start()

    # loop over frames from the video file stream
    while True:
        try:
            # grab the frame from the threaded video stream
            # make a copy of the frame and resize it for display/video purposes
            frame = vs.read()

            # use the NCS to acquire predictions
            # predictions = predict(frame, graph)
            frame_resized = cv2.resize(frame, (299, 299), interpolation=cv2.INTER_CUBIC)
            numpy_frame = np.asarray(frame_resized)
            numpy_frame = cv2.normalize(numpy_frame.astype('float'), None, -0.5, .5, cv2.NORM_MINMAX)
            numpy_final = np.expand_dims(numpy_frame, axis=0)
            print("WTF 0: " + str(numpy_final.shape))
           # graph.queue_inference_with_fifo_elem(inputs, outputs, numpy_final,'object2')
         
            graph.queue_inference_with_fifo_elem(inputs, outputs, numpy_final.astype(np.float32),'object2')
            #MM

            # output, user_obj = output_fifo.read_elem()
            output, user_obj = outputs.read_elem()      # MM
            print('WTF:0 ' +str(output))
            print('WTF: 1 ' + str(user_obj))
            # Print the results
            print('\n------- predictions --------')

            # labels = numpy.loadtxt('./labels.txt', str, delimiter = '\t' )
            labels = np.loadtxt('./categories.txt', str, delimiter = '\t' ) #MM

            order = output.argsort()[::-1][:6]
            for i in range( 0, 5 ):
                print ('prediction ' + str(i) + ' is ' + labels[order[i]])

            # check if we should display the frame on the screen
            # with prediction data (you can achieve faster FPS if you
            # do not output to the screen)
            if args["display"] > 0:
                # display the frame to the screen
                cv2.imshow("Output", image_for_result)
                key = cv2.waitKey(1) & 0xFF

                # if the `q` key was pressed, break from the loop
                if key == ord("q"):
                    break

            # update the FPS counter
            fps.update()

        # if "ctrl+c" is pressed in the terminal, break from the loop
        except KeyboardInterrupt:
            break

        # if there's a problem reading a frame, break gracefully
        except AttributeError:
            break

# stop the FPS counter timer
fps.stop()

# destroy all windows if we are displaying them
if args["display"] > 0:
    cv2.destroyAllWindows()

# stop the video stream
vs.stop()

# clean up the graph and device
graph.DeallocateGraph()
device.CloseDevice()

# display FPS information
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
