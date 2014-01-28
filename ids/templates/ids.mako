<%inherit file="app.mako"/>

##
## define app-level blocks:
##
<%block name="header">
    <a href="${request.route_url('dataset')}">
        <img src="${request.static_url('ids:static/header.gif')}"/>
    </a>
</%block>

<%block name="head">
    <link href="${request.static_url('clld:web/static/css/charissil.css')}" rel="stylesheet">
</%block>

${next.body()}
