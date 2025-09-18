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
	include('inc/albums_functions.php');
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
     <?php
          getWindowTitle()
     ?>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
     <?php
          getStylesheet();
     ?>
</head>
<body>
<?php
getBrowserTitle();
getAlbumsList();
getThanksTo();
?>
</body>
</html>
