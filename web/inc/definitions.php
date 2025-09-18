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

     // Default langage used for navigation (available for now: "fr" and "en")
     // if you feel like translate it to another language, thanks for emailing it to picsphp@smoothplanet.com
     // i'll make it available for everybody. thank you.
     $default_lang="fr";
     
     // The name of your pictures albums, it will appear on the first page and in the browser window
     $my_album="/web";

     // Do you want to display the abstract of the album (if exists) on the index albums list
     // 0=no  1=yes
     $display_abstract=1;
     
     // Is there any folder that should not be browsed and included in the index even if there are pictures ?
     // To add a folder just add it in the array below by using the same format, ie between 'xxxx' and comma separated
     // Everything under a folder will not be browsed ie. if 'x' is in the list, there is no need to add 'x/y'
     $not_browsable_folder=array('inc', 'dev', 'stats', 'cartes', 'css');

     // Filename of the index albums list
     // you may want to change that to index.php but any other name does not make to much change I guess.
     $albums_index_filename="myalbums.php";
     
     # ****************************************************************************************
     # 'Private' functions --- SHOULD NOT BE CHANGED ---
     # ****************************************************************************************
     // used in development,... you should not have to change that
     $debug=0;
     $album_php_config="album_config.php";
     
?>