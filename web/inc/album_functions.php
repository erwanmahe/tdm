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
# Functions that can be called from the album page (album.php)
# ****************************************************************************************
function getAlbumTitle($before="", $after="") {
     echo "<h1 class=\"albumtitle\">$before";
     echo getAlbumTitleText();
     echo "$after</h1>\n";
}

function getAlbumDescription($before="", $after="") {
     $text = getAlbumDescriptionText();
     if ($text!="") {
          echo "<div id=\"albumdescription\">$before$text$after</div>";
     }
}

function getThumbnails() {
     global $files, $album, $lines, $cols, $nbpage, $display_number, $lang;
     $x=0;
     $y=0;
     $startCounter=($nbpage-1)*($lines*$cols);
     # check the value of startCounter...
     if ($startCounter>sizeof($files)) {
          $nbpage=round(sizeof($files)/($lines*$cols));
          $startCounter=(round(sizeof($files)/($lines*$cols))-1)*($lines*$cols);
     }
     echo "<table id=\"thumbnails\">\n";
     while ($x < $lines) {
          echo "   <tr class=\"thumbLine\">\n";
          while ($y < $cols) {
               if ($startCounter<sizeof($files)) {
                    echo "      <td class=\"thumbCell\">";
                    if ($display_number) {
                         echo "$startCounter&nbsp;";
                    }
                    echo "<a href=\"picture.php?album=$album&amp;picture=$startCounter&amp;lang=$lang\">";
                    echo "<img src=\"".getThumbnailPath($files[$startCounter])."\" alt=\"$files[$startCounter]\" ".getThumbnailSize($files[$startCounter])." /></a>";
                    echo "</td>\n";
               } else {
                    echo "      <td class=\"noThumbCell\">&nbsp;</td>\n";
               }
               $y++;
               $startCounter++;
          }
          $x++;
          $y=0;
          echo "   </tr>\n";
     }
     echo "</table>\n";
}

function getPagesNavigation($before="[", $after="]") {
          echo "<div id=\"navigation\">";
          getPreviousPageLink($before, $after);
          getAlbumIndexLink($before, $after);
          getNextPageLink($before, $after);
          echo "<br />\n";
          getPagesIndexLink($before, $after);
          echo "</div>\n";
}

function getPreviousPageLink($before="[", $after="]") {
     global $album, $nbpage, $previous_page, $lang;
     if ($nbpage>1) {
          echo "<span class=\"navigationItem\">";
          echo "<a href=\"album.php?album=$album&amp;nbpage=".($nbpage-1)."&amp;lang=$lang\">&nbsp;&nbsp;$before$previous_page$after&nbsp;&nbsp;</a></span>\n";
     } else {
          echo "<span class=\"navigationItem\">&nbsp;&nbsp;$before$previous_page$after&nbsp;&nbsp;</a></span>\n";
     }
}

function getNextPageLink($before="[", $after="]") {
     global $album, $lines, $cols, $nbpage, $next_page, $files, $lang;
     $lastPage=ceil(sizeof($files)/($lines*$cols));
     if ($nbpage<$lastPage) {
          echo "<span class=\"navigationItem\">";
          echo "<a href=\"album.php?album=$album&amp;nbpage=".($nbpage+1)."&amp;lang=$lang\">&nbsp;&nbsp;$before$next_page$after&nbsp;&nbsp;</a></span>\n";
     } else {
          echo "<span class=\"navigationItem\">&nbsp;&nbsp;$before$next_page$after&nbsp;&nbsp;</a></span>\n";
     }
}

function getAlbumIndexLink($before="[", $after="]") {
     global $index_album, $albums_index_filename, $lang;
     echo "<span class=\"navigationItem\"><a href=\"$albums_index_filename?lang=$lang\">&nbsp;&nbsp;$before$index_album$after&nbsp;&nbsp;</a></span>\n";
}

function getPagesIndexLink($before="[", $after="]") {
     global $album, $lines, $cols, $nbpage, $files, $lang;
     $lastPage=ceil(sizeof($files)/($lines*$cols));
     $x=1;
     while ($x<=$lastPage) {
          if ($x==$nbpage) {
               echo "<span class=\"navigationItem\">&nbsp;&nbsp;$before$x$after&nbsp;&nbsp;</span>\n";
          } else {
               echo "<span class=\"navigationItem\"><a href=\"album.php?album=$album&amp;nbpage=$x&amp;lang=$lang \">&nbsp;&nbsp;$before$x$after&nbsp;&nbsp;</a></span>\n";
          }
          $x++;
     }
}
?>