#include <iostream>
#include <random>
#include <opencv2\core\core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/calib3d.hpp>
#include <map>
#include <math.h>
#include <time.h>
using namespace std;
using namespace cv;
const double M_PI = 3.141592653589793238462643;
const int xSize = 500;
const int ySize = 500;
map<string, int> cnt;
vector< pair<int, string> > v;
Mat img;
inline int srt(pair<int, string> a, pair<int, string> b) {
	return a.first > b.first;
}
inline string fresh(string s) {
	string s2;
	for (auto f : s) {
		if (f >= 'A' && f <= 'Z') s2.push_back(f - 'A' + 'a');
		else if (f >= 'a' && f <= 'z') s2.push_back(f);
	}
	return s2;
}
inline int ptsDist(int x1, int y1, int x2, int y2) {
	return (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2);
}
inline int noCrash(int mx, int my, int r) {
	if (mx - r<0 || mx + r>=xSize || my - r<0 || my + r>=ySize) return 0;
	for (int i = mx - r; i <= mx + r; i++) {
		for (int j = my - r; j <= my + r; j++) {
			if (ptsDist(mx, my, i, j) <= r*r) {
				for (int c = 0; c < 3; c++) {
					//img.data[img.channels()*(img.cols*j+x)+0]
					if (img.at<Vec3b>(j, i)[c] != 255) return 0;
				}
			}
		}
	}
	for (int i = 0; i < xSize; i++) {
		for (int j = 0; j <= ySize + r; j++) {
			if (ptsDist(mx, my, i, j) <= r*r) {
				for (int c = 0; c < 3; c++) {
					if (img.at<Vec3b>(i, j)[c] != 255) return 0;
				}
			}
		}
	}
	return 1;
}
inline int findRad(int r) {
	if (r == v[0].first) return 100;
	else return 100 * r / v[0].first;
}
inline void drawCircle(int mx,int my,int r,string s) {
	cv::circle(img, Point(mx, my), r, Scalar(rand() % 200, rand() % 200, rand() % 200),-1);
	cv::putText(img, s.c_str(), Point(mx-r, my), FONT_HERSHEY_SIMPLEX,(sqrt((r*0.8)/(s.size()*0.6)))/sqrt((s.size()*0.8)),Scalar(0,0,0),2,LINE_AA);
	return;
}

int main() {
	srand(time(NULL));
	img = Mat(xSize, ySize, CV_8UC3, Scalar(255, 255, 255));
	string s;
	freopen("./in2.txt", "r",stdin);
	while (cin >> s) {
		double f;
		s = fresh(s);
		cin >> f;
		if (s.empty()) continue;
		cnt[s] = f*100000;
	}
	for (auto f : cnt) {
		v.push_back(make_pair(f.second, f.first));
	}
	sort(v.begin(), v.end(),srt);
	for (auto f : v) {
		cout << f.second << ' ' << f.first << endl;
	}
	for(int t=0;t<v.size();t++){
		cout << t << "/" << v.size() << endl;
		pair<int, string> f = v[t];
		int nowr = findRad(f.first);
		if (nowr < 5) continue;
		double r = 1;
		while (r <= (xSize>>1)) {
			int key = 0;
			for (int i = 0; i < 10; i++) {
				double angle = rand();
				int nowx = xSize/2+r*(cos(angle));
				int nowy = ySize/2+r*(sin(angle));
				
				if (noCrash(nowx, nowy, nowr)) {
					img;
					drawCircle(nowx, nowy, nowr, f.second);
					key = 1;
					break;
				}
			}
			if (key) break;
			r = r*1.2;
		}
	}
	imwrite("out.png", img);


	
	return 0;
}