<%inherit file="../home_comp.mako"/>
<%namespace name="util" file="../util.mako"/>


<%def name="sidebar()">
    <div class="well">
        <h3>Sidebar</h3>
        <p>
            Content
        </p>
    </div>
</%def>

<h2>${ctx.description}</h2>

<%util:section title="Purpose" id="Purpose" level="4">
The purpose of the IDS is to establish a database where lexical material across the continents
is organized in such a way that comparisons can be made. Historical studies, comparative, and
theoretical linguistic research can be based on this documentation. This is a long term
cooperative project that will go on for the next generation or so and will involve linguists
all over the world. It is aimed towards international understanding and cooperation. This is a
pioneering effort that will have global impact. The purpose also contributes to preserving
information on the little-known and "non-prestigious" languages of the world, many of which
are becoming extinct.
</%util:section>

<%util:section title="Rationale" id="Rationale" level="4">
Information on languages of the world is scattered over all the continents and islands and
published in dozens of languages and scripts. There is need of a database where one can find
comparable material to formulate hypotheses and test and validate those theories. For example,
theories on intercontinental connections have been proposed on the basis of the distribution of
'sweet potato' and yet there is no single source, where words with this meaning can be found in
many languages. Good quantitative and statistical studies are almost impossible to do now in
non-Western languages. The IDS will provide a quantitative base for a scientific approach to
language analysis and comparisons. The IDS will provide the research tools necessary for expanding
studies such as phonological theory, word formation, language change, lexical distribution,
symbolism and onomatopoeia, classification, and other ideas that have to do with history of people
and migrations. The IDS will serve not only as a synonym dictionary but as an index to meaning and
to cultures of various people around the earth.
</%util:section>

<%util:section title="Plan of Series" id="PlanofSeries" level="4">
The IDS series may appear as 1) a volume with 25 or more languages recorded; 2) a fascicle with
5 to 10 languages recorded; 3) in single WordLists, which are archived until enough are gathered
to make up a fascicle or volume. A list of fascicles and volumes in progress is available from the
general editor.
</%util:section>

<%util:section title="Procedure" id="Procedure" level="4">
The IDS is developed in cooperation and complementation with other research projects. Throughout
the world there are linguistic activities from establishing of databases in universities and
think-tanks to publishing grammar series and literacy materials, to individual projects such as the
Tibetan dictionary project. Many projects seek to make linguistic data accessible in a format that
will allow generalizations to be made. The computer now gives us the potential for tying together
linguistic databases. The IDS editors will continue to monitor linguistic activity around the world,
both for choosing the languages for forthcoming compilations and for collaboration with other
research teams.
</%util:section>

<%util:section title="Format" id="Format" level="4">
Each fascicle and volume will be produced in the same format, which will assure the elegance of
having comparable materials. Comparative work in Indo-European (IE) has been carried on over 200
years, and excellent research tools have been produced. This experience forms a basis for similar
research tools to be produced for the pre-literate languages which have been more recently recorded.
Specifically, a model for IDS is A Dictionary of Selected Synonyms in the Principal Indo-European
Languages, comp. by Carl Darling Buck, University of Chicago Press, 1949, 1515 pages. The dictionary
is organized in a topical outline of 23 chapters. The outline has been adapted for the IDS, with the
numbering system generally maintained; and this will remain the same for all the WorldLists. Buck=s
dictionary contains approximately 1200 potential entries (not complete for all languages, of course).
The IDS adaptation contains 1,310 entries. If a form does not exist in a certain area of the world,
the entry is left blank. Loanwords are identified when possible; the IE loanwords can be verified be
checking with the heading (and cross-references). The entries will be given bilingually or trilingually,
with English as the first heading, and the language(s) of the area alongside, for example, South American
Indian Languages, contains English, Portuguese, and Spanish in the main glosses.

The text includes something about the phonology of each language, and highlights the linguistic phenomena
of particular interest in comparative discussions of the family represented. The transcriptions of all
the languages are regularized, to simplify comparative research and to encourage the use of the computer
for future manipulation of data. Bibliographical material is included, directing readers to grammars and
other linguistic works on each language. The text may also include discussions on changes of meaning among
the related languages, showing something of the semantic systems.
</%util:section>

<%util:section title="Compilers" id="Compilers" level="4">
Each fascicle and volume will have a chief editor and a group of language specialists who are the
contributors for each language entered in the dictionary. The actual contributors of language data generally
have a high level of field work and experience in the language. In as much as possible, contributors are
sought who are native speakers of the languages recorded. In addition, the volume editor may choose to have
a group of associate editors or area consultants. The scholars are chosen for their interests in cross-cultural
research and for their skills and willingness to give time and thought to the objectives of the IDS. They are
also chosen for wider presentation of the geographical areas and universities and scholarly groups available.
Much of the data being entered into the dictionary is from unpublished field notes. Since the personnel for
each title are different, several volumes can be in process of compilation at the same time.
</%util:section>

<%util:section title="Choice of Languages" id="Languages" level="4">
The languages chosen for each volume are really defined and are representative of the linguistic features of
the area. Well-established language families will be grouped accordingly. Practical consideration must be
given to: availability of publications and field work; comparative work done; orthographies involved;
coordination with other research; contacts and cooperation of personnel and their expertise. Each language
family that is entered that is entered into a dictionary will be corrected and supported by linguistic experts,
who will be consulted regularly.
</%util:section>

<%util:section title="Plan of Volumes" id="Volumes" level="4">
The production of each fascicle and volume will involve sufficient interaction between the editor and the
language specialists to assure accuracy. During the initial stages of compilation, the editor will acquaint
the collaborators with the outline and organization of the dictionary as a series. The IDS WordList is to
distributed to each language contributor and to the associate editors. As the contributors fill in the WordList,
correspondence with the editor deals with such matters as morpheme division, dialect usage, orthography, and
difficulties in finding the correct translations. Particularly important are the responses from the consultants
regarding information on features of the languages that should be included in the introductory material. The
final stage of this collaboration results in a pre-publication copy which is disseminated to each contributor
for final checking. A time schedule is necessary to keep the production on an orderly course. This is blocked
out for the development of each fascicle to be completed in about three years and a volume in about five years
time.
</%util:section>

<%util:section title="Computer Use" id="Computer" level="4">
The format of IDS lends itself exceptionally well to the use of the computer. The IDS data is stored in a
machine-readable format which will be posted on the internet. This would open an unlimited access to IDS data
for scholars from all over the world, who would be able to use the dictionaries for further research.
</%util:section>

<%util:section title="Origin and History of IDS" id="History" level="4">
The idea for a work such as the IDS came to Mary Ritchie Key while on a Fulbright in Chile in 1975 studying the
semantic grouping in the cognate sets of comparative studies. This was followed by pilot projects at the
University of California, Irvine, using comparative data of recognized language families. In 1982, a computer
science and math major constructed a program which we called ASYNCOG, using three words from C.D.Buck: 'water',
'skin','eat'. Scholars were contacted who were chosen for their interests in cross-cultural research and for
their skills and willingness to give time and thought to the objectives of the dictionary series. In 1984, an
award from the University of California, Irvine Faculty Research Committee to A launch
the Intercontinental Dictionary Series set the series on its way. In 1990, the IDS won an Honourable Mention from
the Rolex Awards for Enterprise, from Switzerland.
</%util:section>

<%util:section title="Further Possibilities" id="Possibilities" level="4">
The obvious and immediate product of this intercontinental enterprise is a dictionary series. There are other
imaginable advantages. An IDS centre would serve as a clearinghouse for comparative work between the continents.
It could also serve a repository for scholars to leave their unpublished materials in a place where they would be
appreciated and utilized in further research. Thus, it would assure preservation and continuity of unpublished
work-in-progress. And finally, it will bring together data on the languages of the world, in such away that will
give importance to all languages. This speaks to the unity of all the peoples on earth.
</%util:section>
