#!/bin/bash
OPENCV_DIR=~/Projects/opencv
OPENCV_CONTRIB_DIR=~/Projects/opencv_contrib
OPENCV_INSTALL_DIR=$PWD

echo "Building OpenCV."

pushd $OPEN_CV_DIR
rm -rf build
mkdir build

# Set proper search paths needed for building. 
export PKG_CONFIG_PATH=$OPENCV_INSTALL_DIR/lib/pkgconfig/:${PKG_CONFIG_PATH}
export LIBRARY_PATH=$OPENCV_INSTALL_DIR/lib/:${LIBRARY_PATH}
export LD_LIBRARY_PATH=$OPENCV_INSTALL_DIR/lib/:${LD_LIBRARY_PATH}

# Set environment variables in the proper location based upon OS.
echo "Setting environment variables for vendor opencv library directory."
MARKER_STRING="# Adding vendor opencv directories."
UNAMESTR=`uname`

# PY2_PACKAGES_PATH specifies where to install cv2.so.
PY2_PACKAGES_PATH=${OPENCV_INSTALL_DIR}/lib/
PY2_LIBRARY_PATH=/usr/bin/
PY2_INCLUDE_DIR_path=/usr/include/python2.7/
PY3_PACKAGES_PATH=${OPENCV_INSTALL_DIR}/lib/
PY3_LIBRARY_PATH=/usr/bin/
PY3_INCLUDE_DIR_path=/usr/include/python3.5m/

pushd ./build

# Put build files in release folder.
cmake -D CMAKE_BUILD_TYPE=DEBUG \
-D CMAKE_INSTALL_PREFIX=$OPENCV_INSTALL_DIR \
-D BUILD_opencv_java=OFF \
-D BUILD_opencv_python2=OFF \
-D BUILD_opencv_python3=ON \
-D OPENCV_EXTRA_MODULES_PATH=$OPENCV_CONTRIB_DIR/modules/ \
-D INSTALL_PYTHON_EXAMPLES=ON \
-D INSTALL_C_EXAMPLES=OFF \
-D BUILD_EXAMPLES=ON \
-D PYTHON3_PACKAGES_PATH=${PY3_PACKAGES_PATH} \
-D PYTHON3_LIBRARY=${PY3_LIBRARY_PATH} \
-D PYTHON3_INCLUDE_DIR=${PY3_INCLUDE_DIR_path} \
-D PYTHON2_PACKAGES_PATH=${PY2_PACKAGES_PATH} \
-D PYTHON2_LIBRARY=${PY2_LIBRARY_PATH} \
-D PYTHON2_INCLUDE_DIR=${PY2_INCLUDE_DIR_path} \
-D ENABLE_PRECOMPILED_HEADERS=OFF \
-D WITH_GTK=ON \
-D WITH_GTK_2_X=ON \
-D WITH_1394=OFF \
..

# Check if cmake actually worked
if [ $? -ne 0 ] ; then
	echo "ERROR! CMake seems to have failed!"
	return -1
fi

# Go go go!!!
make -j 4

# Check if make actually worked
if [ $? -ne 0 ] ; then
	echo "ERROR! Make seems to have failed!"
	return -1
fi

# Now finish him!
make install

# Check if make actually worked
if [ $? -ne 0 ] ; then
	echo "ERROR! Make install seems to have failed!"
	return -1
fi

popd # build
popd # $OPENCV_DIR

echo "cv2.so installed to ${OPENCV_INSTALL_DIR}/lib. Copy to appropriate system directory for Python site-packages if necessary."
