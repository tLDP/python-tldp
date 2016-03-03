<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<!-- TLDP Chapters HTML XSL; break source into one output file per chapter
     This is a small customization layer on top of upstream
     docbook-xsl-stylesheets.  Since the XML_CATALOG_FILES will locate the
     installed version of the required import resources, we will use the
     system identifier in the xsl:import line.
  -->
<xsl:import href="http://docbook.sourceforge.net/release/xsl/current/html/chunk.xsl"/>
<xsl:import href="tldp-common.xsl"/>

<!-- Generate a separate HTML page for each preface, chapter or
     appendix.  Contrast this behavior with the tldp-one-page.xsl
     and tldp-section.xsl customizations. -->
<xsl:param name="chunk.section.depth" select="0"></xsl:param>

</xsl:stylesheet>
