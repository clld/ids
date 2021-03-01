<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>
<%block name="title">Word "${ctx}"</%block>

<h2>Word <span class="charissil">${ctx}</span></h2>

% if ctx.alt_name and ctx.alt_description:
  <table class="table table-nonfluid">
    <thead>
      <tr>
      % if len(ctx.alt_name.split(', ')) > 1:
        <td><b>Meaning</b></td>
      % endif
      % if ctx.language.dictionary.alt_representation:
        % for r in ctx.language.dictionary.alt_representation.split(';'):
          <td>${r or ''}</td>
        % endfor
      % endif
      </tr>
    </thead>
    <tbody>
      % for i, an in enumerate(ctx.alt_name.split(', ')):
        <tr>
        % if len(ctx.alt_name.split(', ')) > 1:
          <td>${h.link(request, ctx.counterparts[i].valueset.parameter)}</td>
        % endif
        % for an_ in an.split(';'):
          <td>${an_}</td>
        % endfor
        </tr>
      % endfor
    <tbody>
  </table>
% endif

<h4>Meanings</h4>
<ul>
% for i, value in enumerate(ctx.counterparts):
    <li>${h.link(request, value.valueset.parameter)}</li>
% endfor
</ul>

<hr />
% if u.has_any_comments(ctx.counterparts):
  <h5>Comment</h5>
  % if u.has_same_comments(ctx.counterparts):
    <p>${u.parse_comment_for_meaning_links(request, ctx.counterparts[0].comment, ctx.language.id)|n}</p>
  % else:
  <table class="table table-nonfluid">
    % if ctx.language.dictionary.default_representation:
    <thead>
      <tr>
        <td>Meaning</td>
        <td>Comment</td>
      </tr>
    </thead>
    % endif
    <tbody>
      % for i, value in enumerate(ctx.counterparts):
        % if value.comment:
        <tr>
          <td>${h.link(request, value.valueset.parameter)}</td>
          <td>${u.parse_comment_for_meaning_links(request, value.comment, ctx.language.id)|n}</td>
        </tr>
        % endif
      % endfor
    </tbody>
  </table>
  % endif
% endif

<%def name="sidebar()">
<div class="well well-small">
<dl>
    <dt class="contribution">Language:</dt>
    <dd class="contribution">
        ${h.link(request, ctx.language)}
    </dd>
</dl>
</div>
</%def>
