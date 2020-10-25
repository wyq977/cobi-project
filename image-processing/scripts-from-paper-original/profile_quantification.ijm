 /*  
 *   28.11.2017, ImageJ macro for quantifying intensity in selected rectangular ROIs
 *   Script #2 in "Measuring dorsoventral pattern and morphogen signaling activity profiles in the growing neural tube"
 *   in Methods of Molecular Biology
 *   Anna Kicheva, Marcin Zagorski
 */

/***Rotate image if necessary***/
  setTool("arrow");	
  waitForUser("Image rotation","Specify an arrow from the floor plate region to the roof plate region. The image is rotated so the objects oriented similarly\nto the arrow become vertical. If no arrow is specified the image is not rotated. Press ok when ready.");
   getLine(x1, y1, x2, y2, width);
   getDimensions(width, height, channels, slices, frames);
   nCH = channels;
   nSL = slices;				//can be useful when rotating whole stack (nSL=1 for projections)
   if (x1!=-1){
	      angle = (180.0/PI)*atan2(y1-y2, x2-x1)-90;
	      Stack.getPosition(ch0,sl0,fr0);
	  	  for (i=1; i<nSL+1; i++){
	  	  	  Stack.setSlice(i);
	  	  	  for (j=1; j<nCH+1; j++){
		  	  	  	Stack.setChannel(j);
		  	  	  	run("Rotate...", "angle="+angle+" interpolate");
	  	  	  }
   		  }
    	  Stack.setPosition(ch0,sl0,fr0);
  	  	  print("Image rotated by ",-angle, "degrees left.");
   }
   setTool("rectangle");	
  	 	  
/***Prompting user to specify ROIs***/
   roiManager("count");			//invoke roiManager if it is closed
   waitForUser("ROI specification","Specify one or more rectangular ROIs to be analysed. Press 't' to add ROI to ROI manager or update already present ROI.\nThe script quantifies the intensity profiles along the y-axis of all ROIs present in the ROI manager. Press ok when ready.");
   kROIS = roiManager("count"); //count number of ROIs in the ROI manager. If no ROIs exit the script	
   if (kROIS == 0){
   		exit("No ROIs present in the ROI manager. Terminating the macro.");
   }
   		
/***Specify labels and image title***/   
   labels = newArray(nCH);			//default labels; modify here to have different default labels
   for (i=0; i<nCH; i++) {
  		labels[i] = "ch"+i+1;
   }
   title = getTitle();				//by default the title of active image with additional suffix is used to save results
   print("Image analysed:",title);
   if( endsWith(title, ".tif") ){	
   		title = replace( title, ".tif", "");	//removes ".tif" from the title; so the title is used with different types (.tif, .txt, ...)
   }
/***Selecting directory to save results***/ 
   dir = getDirectory("Select a directory to save results");	//Select existing directory or create a new one
   dirROIS = dir+File.separator+"rois";						//ROIs are stored here
   dirPROJ = dir+File.separator+"projections";				//Projections (.tiff) are stored here
   File.makeDirectory(dirROIS);								//make these directories if they don't exist
   File.makeDirectory(dirPROJ);

/***Quantifying profiles and saving results***/ 
   kROIS = roiManager("count");	
   getPixelSize(unit, pixelWidth, pixelHeight);
  
   for (k = 0; k < kROIS; k++){
	  	roiManager("Select", k);
	  	Roi.getBounds(xr, yr, widthROI, heightROI);
	  	print("ROI no.",k,"width:",widthROI*pixelWidth,"[um], height:",heightROI*pixelHeight,"[um]");
		run("Clear Results");
		
		for(m = 0; m < nCH; m++){
				Stack.setDisplayMode("color");
				Stack.setChannel(m+1);
				setKeyDown("alt"); 
				profile = getProfile();
				for (i = 0; i < profile.length; i++){
					  setResult("DVposition(um)", i, i*pixelHeight); 		
				      //setResult(labels[m], i, profile[i]);	//quantify from D to V		
				      setResult(labels[m], i, profile[profile.length - i - 1]);	//quantify from V to D
				}
				updateResults;
		}
	
		selectWindow("Results");
	  	save(dir + File.separator + title + "-" + k + ".txt");		//by default results file name has suffix indicating corresponding ROI
	  	run("Clear Results");
   }

/***Saving ROIs and .tif projection***/ 
   roiManager("Deselect");
   roiManager("Save", dirROIS + File.separator + title + ".zip");		//saving ROIs
   saveAs("Tiff", dirPROJ + File.separator + title + ".tif");			//saving active image

/***Updating Log window***/
   selectWindow("Log");
   print("Number of ROIs analysed:",kROIS);
   print("Number of channels analysed for each ROI:",nCH);	
   print("Results saved in directory:", dir);
