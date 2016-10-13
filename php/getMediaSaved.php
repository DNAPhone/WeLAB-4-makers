<?php

    define('BASE_DIR', dirname(__FILE__));
    require_once(BASE_DIR.'/config.php');

    global $sortOrder;
    global $showTypes;

    switch($_GET['action']){ 

        case 'deleteAllMedia':
            
            $files = scandir(MEDIA_PATH, $sortOrder - 1);

            foreach($files as $file) {
                if($file != '.' && $file != '..') {
                    unlink(MEDIA_PATH . "/$file");
                }
            }
            
            echo "deleted";
            break;
            
        case 'deleteMedia':
            unlink(MEDIA_PATH . "/".$_GET['mediaToBeDeleted']);
            echo "deleted";
            break;
        
        case 'getImages':
            
            $files = scandir(MEDIA_PATH, $sortOrder - 1);
            
            // If no image is available, MEDIA_PATH contains only '.' and '..', so its length is 2. Thus, the following while waits until the image has been saved. The library saves 2 images each time the user asks to save a photo. One is low-res, the other is hi-res, so the dir must have at least 4 elements.
            while (count($files) < 4)
                $files = scandir(MEDIA_PATH, $sortOrder - 1);

            $text = "\"";

            foreach($files as $file) {
                if($file != '.' && $file != '..') {

                    // The library saves 2 images each time the user asks to save a photo. One is the thumbnail and is named name.jpg.number.jpg
                    // The other is named name.jpg. Thus splitting the name with respect to .jpg returns an array having size 3 for the
                    // thumbnail, and 2 for the other one. Thus, the thumbnail can be deleted with the PHP unlink function.
                    if (count(explode(".jpg", $file)) > 2)
                        unlink(MEDIA_PATH . "/$file");

                    else {
                        if ($text == "\"")
                            $text = $text.$file;
                        else
                            $text = $text."|".$file;
                    }
                }
            }

            $text = $text."\"";
            echo $text;
            break;
        
        case 'getVideos':
            
            $files = scandir(MEDIA_PATH, $sortOrder - 1);
            
            $saved = false;
            
            // If no image is available, MEDIA_PATH contains only '.' and '..', so its length is 2. Thus, the following while waits until the movie has been saved. The library saves 2 elements each time the user asks to save a movie. One is the thumbnail, the other is the movie, so the dir must have at least 4 elements.
            while (count($files) < 4 or !$saved) {
                $files = scandir(MEDIA_PATH, $sortOrder - 1);
                
                $saved = true;
                
                foreach($files as $file) {
                    
                    // The library creates a temporary name.mp4.h264 file, that becomes name.mp4 when it is saved. Thus, the following code checks if a file whose name includes .h264 exists and waits for it to disappear.
                    if (strpos($file, '.h264') !== false) {
                        $saved = false;
                        break;
                    }
                    
                }
            }

            $text = "\"";

            foreach($files as $file) {
                if($file != '.' && $file != '..') {

                    // The library saves 2 videos each time the user asks to save a photo. One is the thumbnail and named name.mp4.number.jpg
                    // The other is named name.mp4. Thus splitting the name with respect to .jpg returns an array having size 2 for the
                    // thumbnail, and 0 for the other one. Thus, the thumbnail can be deleted with the PHP unlink function.
                    if (count(explode(".jpg", $file)) > 1)
                        unlink(MEDIA_PATH . "/$file");

                    else {
                        if ($text == "\"")
                            $text = $text.$file;
                        else
                            $text = $text."|".$file;
                    }
                }
            }

            $text = $text."\"";
            echo $text;
            break;
    }  
   
?>