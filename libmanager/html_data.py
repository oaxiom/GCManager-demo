#
# (c) 2024 Helixiome, all rights reserved.
# (c) 2024 中基科生物保留所有权利
#
# Author(s):
# Andrew P. Hutchins
#

helix_logo = '''
data:image/png;base64,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
'''

style_sheet = '''

:root,
::backdrop {
  /* Set sans-serif & mono fonts */
  --sans-font: -apple-system, BlinkMacSystemFont, "Avenir Next", Avenir,
    "Nimbus Sans L", Roboto, "Noto Sans", "Segoe UI", Arial, Helvetica,
    "Helvetica Neue", sans-serif;

  --standard-border-radius: 5px;

  --text #111a1a;
  --blue: #2C5274;
  --green: #6DB794;
  --tab-grey-bg: #E1E5EB;
  --bg: #fff;
  --border: #898EA4;
}

/* Reset box-sizing */
*, *::before, *::after {
  box-sizing: border-box;
}

/* Reset default appearance */
textarea,
select,
input,
progress {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
}

html {
  /* Set the font globally */
  font-family: var(--sans-font);
  scroll-behavior: smooth;
}

/* Make the body a nice central block */
body {
  color: var(--text);
  background-color: var(--bg);
  font-size: 0.9rem;
  line-height: 1.4;

  margin: 4%;
}
body > * {
  grid-column: 2;
}

/* override styles when printing */
@media print {
  body {
    font-size: 0.2rem;
  }
}

/* Add a little padding to ensure spacing is correct between content and header > nav */
main {
  padding-top: 1.5rem;
}

body > footer {
  margin-top: 4rem;
  padding: 2rem 1rem 1.5rem 1rem;
  color: var(--text-light);
  font-size: 0.9rem;
  text-align: center;
  border-top: 1px solid var(--border);
}

/* Format headers */
h1 {
  color: var(--blue);
  font-size: 2rem;
}

h2 {
  color: var(--blue);
  font-size: 1.5rem;
  margin-top: 0.1rem;
}

h3 {
  color: var(--blue);
  font-size: 1.5rem;
  margin-top: 0.05rem;
}

h4 {
  color: var(--blue);
  font-size: 1.4rem;
}

h5 {
  color: var(--blue);
  font-size: 1.1rem;
}

h6 {
  color: var(--blue);
  font-size: 0.9rem;
}

p {
  margin-top: 0.1rem 0;
}

/* Prevent long strings from overflowing container */
p, h1, h2, h3, h4, h5, h6 {
  overflow-wrap: break-word;
}

/* Fix line height when title wraps */
h1,
h2,
h3 {
  line-height: 0.3;
}

/* Format tables */
table {
  border-collapse: collapse;
  margin: 1.5rem 0;
}

td,
th {
  border: 1px solid var(--border);
  text-align: start;
  padding: 0.4rem;
}

th {
  background-color: var(--tab-grey-bg);
}

table caption {
  margin-bottom: 0.5rem;
}

/* Misc body elements */
hr {
  border: none;
  height: 2px;
  background: var(--blue);
  color: var(--blue);
  margin: 1rem auto;
}

div[style*="flex"] {
  align-items: baseline;
}


'''


    # As can't escape {} in f string?
rounded_rects_styles = '''
    .rounded-rectangleL {
    width: 200px;
    height: 15px;
    background-color: #FFFFFF;
    border-radius: 2px;
    }
    .rounded-rectangleR {
    right: 0px;
    width: 200px;
    height: 15px;
    background-color: #FFFFFF;
    border-radius: 2px;
    }
    '''
