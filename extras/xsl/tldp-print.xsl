<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<!-- TLDP Print XSL; generate Formatting Objects (FO) for print outputs
     This is a small customization layer on top of upstream
     docbook-xsl-stylesheets.  Since the XML_CATALOG_FILES will locate
     the installed version of the required import resources, we will use
     the system identifier in the xsl:import line.
  -->
<xsl:import href="http://docbook.sourceforge.net/release/xsl/current/fo/docbook.xsl"/>

<!-- Number all sections in the style of 'CH.S1.S2 Section Title' where
     CH is the chapter number,  S1 is the section number and S2 is the
     sub-section number.  The lables are not limited to any particular
     depth and can go as far as there are sections. -->
<xsl:param name="section.autolabel" select="1"></xsl:param>
<xsl:param name="section.label.includes.component.label" select="0"></xsl:param>

<!-- Turn off the default 'full justify' and go with 'left justify'
     instead.  This avoids the large gaps that can sometimes appear
     between words in fully-justified documents.  -->
<xsl:param name="alignment">start</xsl:param>

<!-- Shade Verbatim Sections such as programlisting and screen -->
<xsl:param name="shade.verbatim" select="1"/>

<!-- Create bookmarks in .PDF files -->
<xsl:param name="fop.extensions" select="0"/>

<!-- Use fop1 extensions, per 
     https://lists.oasis-open.org/archives/docbook-apps/201110/msg00080.html
  -->
<xsl:param name="fop1.extensions" select="1"/>
                                                                                
</xsl:stylesheet>
