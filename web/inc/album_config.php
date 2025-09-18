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

     # ****************************************************************************************
     # 
     # ****************************************************************************************
     # number of lines and columns per page for the pictures index
     $lines=2;
     $cols=2;
     
     # Do you want to display a number besides the thumbnail ?
     # 1: yes, 2: no
     $display_number=1;
     
     # What stylesheets should you use for you albums ?
     # You might define more than one, it is 'cascading' stylesheet :-)
     # Make sure the stylesheet you need is in "inc/css/".
     $album_stylesheets=array('default.css');
     
     # Are the thumbnails available somewhere ? 
     # 1: yes, 0: no
     # If not the original pictures will be resized by the browser (not suitable)!
     $thumb=1;

     # if yes, which repertory are they ? and what is the 'prefix' of the thumbnails ?
     $thumb_dir="";
     $thumb_prefix="mini_";

     # if not, what percentage the thumbnails should be ?
     # 100%= the thumbnails are the same size than the picture itself.
     # 50%=half of the original size
     # 0%=not a valid value
     $thumb_resize=50;
     
     # ****************************************************************************************
     # 
     # ****************************************************************************************
     $nb_thumb_navigation=5;
     
     
?>
