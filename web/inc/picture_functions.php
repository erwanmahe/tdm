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

if ($album=="") {
     $files = getFileList(".");
} else {
     $files = getFileList($album);
}

# ****************************************************************************************
# Functions that can be called from the picture page (picture.php)
# ****************************************************************************************
function getPictureTitle() {
     echo "<h1 class=\"picturetitle\">";
     echo getPictureTitleText();
     echo "</h1>\n";
}

function getPictureDescription() {
     $text = getPictureTitleDescriptionText();
     if ($text!="") {
          echo "<div id=\"picturedescription\">\n$text</div>\n";
     }
}

function getPicture() {
     global $album, $files, $picture;
     echo "<div class=\"picture\">";
     echo "<img src=\"$album/$files[$picture]\" alt=\"$files[$picture]\" ".getPictureSize($files[$picture])." />";
     echo "</div>\n";
}

function getTextNavigation($before="[", $after="]") {
     global $album, $index_thumbnail, $previous_picture, $next_picture, $first_picture, $last_picture, $files, $picture, $lang;
     echo "<div id=\"textnavigation\">";
     if ($picture>0) {
          echo "<span class=\"navigationItem\"><a href=\"picture.php?album=$album&amp;picture=".($picture-1)."&amp;lang=$lang \">&nbsp;$before$previous_picture$after&nbsp;</a></span>\n";
     } else {
          echo "<span class=\"navigationItem\">&nbsp;$before$previous_picture$after&nbsp;</a></span>\n";
     }
     if ($picture<(sizeof($files)-1)) {
          echo "<span class=\"navigationItem\"><a href=\"picture.php?album=$album&amp;picture=".($picture+1)."&amp;lang=$lang \">&nbsp;$before$next_picture$after&nbsp;</a></span><br />\n";
     } else {
          echo "<span class=\"navigationItem\">&nbsp;$before$next_picture$after&nbsp;</a></span><br />\n";
     }
     if ($picture>0) {
          echo "<span class=\"navigationItem\"><a href=\"picture.php?album=$album&amp;picture=0&amp;lang=$lang \">&nbsp;$before$first_picture$after&nbsp;</a></span>\n";
     } else {
          echo "<span class=\"navigationItem\">&nbsp;$before$first_picture$after&nbsp;</span>\n";
     }
     echo "<span class=\"navigationItem\"><a href=\"album.php?album=$album&amp;nbpage=1&amp;lang=$lang \">&nbsp;$before$index_thumbnail$after&nbsp;</a></span>\n";
     if ($picture<(sizeof($files)-1)) {
          echo "<span class=\"navigationItem\"><a href=\"picture.php?album=$album&amp;picture=".(sizeof($files)-1)."&lang=$lang \">&nbsp;$before$last_picture$after&nbsp;</a></span>\n";
     } else {
          echo "<span class=\"navigationItem\">&nbsp;$before$last_picture$after&nbsp;</span>\n";
     }
     echo "</div>\n";
}

function getThumbnailsNavigation() {
     global $nb_thumb_navigation, $album, $thumb_dir, $thumb_prefix, $thumb_resize, $files, $picture, $lang;
     echo "<table id=\"thumbnailsNavigation\">\n<tr>\n";
     $i=0;
     $start=$picture-(round($nb_thumb_navigation/2)-1);
     while ($i<$nb_thumb_navigation) {
          if (($start<0) or ($start>(sizeof($files)-1))) {
               echo "<td align=\"center\" valign=\"middle\">&nbsp;</td>\n";
          } else {     
               echo "<td align=\"center\" valign=\"middle\"><a href=\"picture.php?album=$album&picture=".($start)."&lang=$lang \"><img src=\"".getThumbnailPath($files[$start])."\" alt=\"$files[$start]\" ".getThumbnailSize($files[$start])."/></a></td>\n";
          }
          $start++;
          $i++;
     }
     echo "</tr>\n</table>\n";
}

?>