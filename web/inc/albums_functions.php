<?php
/*
     ------------------------------------------------------------------------------------
    Copyright (C) 2002, 2003 Jerome Chevillat
    Contact: jerome@chevillat.ch, contact@smoothplanet.com
     ------------------------------------------------------------------------------------

    This file is part of picsPHP.

    picsPHP is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    picsPHP is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with picsPHP; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
    
*/
?>
<?php
include_once('inc/definitions.php');
include_once('inc/functions.php');

# Load the default album config file
include("inc/album_config.php");
# Load overidden album config file if exists
if (file_exists("$album/$album_php_config")) {
     include("$album/$album_php_config");
}

include_once("inc/lang_$lang.php");

# ****************************************************************************************
# Functions that can be called from the album browser page (index.php)
# ****************************************************************************************

function getAlbumsList($before="", $after="") {
     global $browse;
     echo "<div id=\"albumbrowser\">\n$before";
     traverse($browse);
     echo "$after</div>";
}

function getBrowserTitle($before="", $after="") {
     global $my_album;
     echo "<h1 class=\"titlebrowser\">$before$my_album$after</h1>\n";
}

# ****************************************************************************************
# 'Private' functions
# ****************************************************************************************

function traverse($starting_directory, $toBePrinted="") {
     global $display_abstract, $album_php_config, $lang;

     $to_print="";
     include('inc/album_config.php');

     $directory_link=$starting_directory;
     if ($directory_link==".") {
          $directory_link="";
     }

     if (file_exists("$directory_link$album_php_config")) {
          include("$directory_link$album_php_config");
     }
     
     $is_picture_directory=false;
     $down_printed=false;
     $all_dir = array();
     if($d_obj = dir($starting_directory)) { 
          while($this_entry = $d_obj->read()) { 
               if ($this_entry != "." && $this_entry != ".." && $this_entry != $thumb_dir) { 
                    if(is_dir("$directory_link$this_entry")) {
                         if (isValidPictureDirectory("$directory_link$this_entry")) { 
                              $all_dir[] = $this_entry;
                         }
                    }
                    if (is_file("$directory_link$this_entry")) {
                         if (isValidPictureFile("$directory_link$this_entry")) {
                              $is_picture_directory=true;
                         }
                    }     
               }
          } 
          $d_obj->close(); 
     } else {
          echo "Error!  Couldn't list directory $starting_directory for some reason!<br />";
          exit;
     }
     $abstract="";
     if ($display_abstract) {
          $abstract=getAlbumDescriptionText("$directory_link");
     }
     if ($is_picture_directory) {
          echo $toBePrinted;
          $to_print .= "<ul>\n<li><a href=\"album.php?album=";
          $to_print .=  substr($directory_link, 0, strlen($directory_link)-1);
          $to_print .= "&lang=$lang\">";
          $to_print .= getAlbumTitleText("$directory_link");
          $to_print .= "</a><div class=\"abstractalbum\">$abstract</div></li>\n";
          echo $to_print;
          $to_print ="";
     }
     else {
          $to_print .= $toBePrinted."<ul>\n<li>";
          $to_print .= getAlbumTitleText("$starting_directory");
          $to_print .= "<div class=\"abstractalbum\">$abstract</div></li>\n";
     }
     $is_down_pictures=0;
     if (sizeof($all_dir)!=0) {
          $i=0;
          sort($all_dir);
          while ($i<sizeof($all_dir)) {
               $tmp_is_picture=0;
               $tmp_is_picture = traverse("$directory_link$all_dir[$i]/", $to_print);
               if ($tmp_is_picture) {
                    $to_print="";
               }
               $is_down_pictures = $is_down_pictures | $tmp_is_picture;
               $i++;
          }
     }
     if ($is_picture_directory | $is_down_pictures) {
          echo "</ul>\n";
     }
     return ($is_down_pictures or $is_picture_directory);
}
?>