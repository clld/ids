<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>
<%block name="title">${ctx.language} - "${ctx.parameter}"</%block>

<h2>Words in ${h.link(request, ctx.language)} for meaning ${ctx.parameter.id} "${h.link(request, ctx.parameter)}"</h2>

<table class="table table-nonfluid">
  % if ctx.language.dictionary.default_representation:
  <thead>
    <tr>
      <td>${ctx.language.dictionary.default_representation}</td>
      % if ctx.language.dictionary.alt_representation:
      <td>${ctx.language.dictionary.alt_representation}</td>
      % endif
    </tr>
  </thead>
  % endif
  <tbody>
    % for i, value in enumerate(ctx.values):
    <tr>
      <td>${h.link(request, value.word, class_='charissil')}</td>
      % if ctx.language.dictionary.alt_representation:
      <td class="charissil">${value.word.alt_name or ''}</td>
      % endif
    </tr>
    % endfor
  </tbody>
</table>

<hr />

% if u.has_any_comments(ctx.values):
  <h5>Comment</h5>
  % if u.has_same_comments(ctx.values):
    <p>${u.parse_comment_for_meaning_links(request, ctx.values[0].comment, ctx.language.id)|n}</p>
  % else:
  <table class="table table-nonfluid">
    % if ctx.language.dictionary.default_representation:
    <thead>
      <tr>
        <td>${ctx.language.dictionary.default_representation}</td>
        <td>Comment</td>
      </tr>
    </thead>
    % endif
    <tbody>
      % for i, value in enumerate(ctx.values):
        % if value.comment:
        <tr>
          <td>${h.link(request, value.word, class_='charissil')}</td>
          <td>${u.parse_comment_for_meaning_links(request, value.comment, ctx.language.id)|n}</td>
        </tr>
        % endif
      % endfor
    </tbody>
  </table>
  % endif
% endif

% if u.any_org_value_differ(ctx.values):
  <h5>Original IDS Data</h5>
  % if u.has_same_org_values(ctx.values):
    <p>${ctx.values[0].org_value or ''}</p>
  % else:
  <table class="table table-nonfluid">
    % if ctx.language.dictionary.default_representation:
    <thead>
      <tr>
        <td>${ctx.language.dictionary.default_representation}</td>
        <td>Original Value</td>
      </tr>
    </thead>
    % endif
    <tbody>
      % for i, value in enumerate(ctx.values):
      <tr>
        <td>${h.link(request, value.word, class_='charissil')}</td>
        <td>${value.org_value or ''}</td>
      </tr>
      % endfor
    </tbody>
  </table>
  % endif
% endif

<%def name="sidebar()">
<div class="well well-small">
<dl>
  <dt class="contribution">${_('Contribution')}:</dt>
  <dd class="contribution">
    ${h.link(request, ctx.contribution)}
    by
    ${h.linked_contributors(request, ctx.contribution)}
    ${h.cite_button(request, ctx.contribution)}
  </dd>
  <dt class="parameter">${_('Parameter')}:</dt>
  <dd class="parameter">${h.link(request, ctx.parameter)}</dd>
</dl>
</div>
</%def>
