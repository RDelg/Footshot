#include <cv.h>
#include <highgui.h>
#include <iostream>
using namespace std;
using namespace cv;

int main(){
	
	VideoCapture cam(0);

	if (!cam.isOpened()){
		cout << "Oopsie" << endl;
		return -1;
	}

	while(true){
		Mat frame;
		cap >> frame;

		if (frame.empty()) break;

		imshow("Frame", frame);
		char c = (char)waitKey(1);

		if (c == 27) break;
	}

	cam.release();
	destroyAllWindows();

	return 0;
}