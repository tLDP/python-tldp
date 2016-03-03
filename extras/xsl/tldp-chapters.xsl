<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:import href="/usr/share/xml/docbook/stylesheet/nwalsh/html/chunk.xsl"/>
<xsl:import href="tldp-common.xsl"/>

<!-- Generate a separate HTML page for each preface, chapter or
     appendix.  Contrast this behavior with the tldp-one-page.xsl
     and tldp-section.xsl customizations. -->
<xsl:param name="chunk.section.depth" select="0"></xsl:param>

</xsl:stylesheet>
