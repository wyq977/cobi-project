/*  
 *   28.11.2017, ImageJ macro for max z-stack projection in batch mode
 *   Script #1 in "Measuring dorsoventral pattern and morphogen signaling activity profiles in the growing neural tube"
 *   in Methods of Molecular Biology
 *   Anna Kicheva, Marcin Zagorski
 */

dirImages = getDirectory("Select input folder with images");
dirProjections = getDirectory("Select output folder for projections");

setBatchMode(true); 									//enter batch mode
list = getFileList(dirImages);
for (i = 0; i < list.length; i++)
        open(dirImages + File.separator + list[i]);		//open all files in the folder

imgArray = newArray(nImages); 							//create an array to operate with images
for (i = 0; i < nImages; i++){ 
 	selectImage(i+1); 
 	imgArray[i] = getImageID();
} 
 
for (i=0; i < imgArray.length; i++) { 
	selectImage(imgArray[i]); 
	Stack.getDimensions(width, height, channels, slices, frames);		  //gets number of slices
	run("Z Project...", "start=1 stop=slices projection=[Max Intensity]");//max z-stack projection
	title = getTitle();													  //getting image title			
	saveAs("TIFF",dirProjections + File.separator + title);			//saving projections
	selectImage(imgArray[i]); 
	run("Close");										//close all non-image windows		
	close();											//close active image
}
setBatchMode(false);									//leave batch mode
 
