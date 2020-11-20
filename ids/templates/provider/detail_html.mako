<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "providers" %>
<%block name="title">${_('Providers')} - ${ctx.name}</%block>

<h3>${ctx.name}</h3>

<dl>
% if ctx.description:
  <dt>Cite:</dt>
  <dd>${ctx.description}</dd>
% endif
% if ctx.accessURL:
  <dt>Data URL:</dt>
  <dd>${h.external_link(url=ctx.accessURL, label=ctx.accessURL, target="_new")}</dd>
% endif
% if ctx.dictionaries:
  <dt>${_("Contributions")}:</dt>
  <dd>
    <ul>
      % for d in sorted(ctx.dictionaries, key=lambda i: i.name):
      <li>${h.link(request, d)}</li>
      % endfor
    </ul>
  </dd>
% endif
%if ctx.license:
  <dt>License:</dt>
  <dd>${h.maybe_license_link(request, ctx.license)}</dd>
% endif
</dl>
