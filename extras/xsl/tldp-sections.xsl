<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:import href="/usr/share/xml/docbook/stylesheet/nwalsh/html/chunk.xsl"/>
<xsl:import href="tldp-common.xsl"/>

<!-- Generate a separate HTML page for each section.  Doing this
     divides the document into many pages with a shorter amount of
     text on each page.  Shorter pages result in less scrolling when
     viewing the document in a web browser.  Contrast this behavior
     with the tldp-chapter.xsl and tldp-one-page.xsl customizations. -->
<xsl:param name="chunk.section.depth" select="1"></xsl:param>

<!-- Make sure that the chapter table of contents is on its own page
     rather than being placed on the same chuck as the first section. -->
<xsl:param name="chunk.first.sections" select="1"></xsl:param>

</xsl:stylesheet>
