"""
Build-time generator: creates films/{slug}.html for every film in FILMS.
Run once; output HTML is committed and hand-editable thereafter.
"""

import os
import html
from pathlib import Path

FILMS = [
    # Short Films first
    {
        "slug": "tuned-in",
        "title": "Tuned In",
        "category": "Short Film",
        "year": "2024",
        "role": "Gaffer, Assistant Colorist",
        "music": None,
        "external_url": "https://mediaspace.wisc.edu/media/Tuned+In/1_behxmrob",
        "external_host": "UW Madison Mediaspace",
        "body": [
            'My senior capstone project. For this class, you vote on roles and scripts, and then get assigned to one of two groups of nine advanced production students. I was the gaffer and assistant colorist.',
            'Despite the intense workload — equivalent in credits to two entire classes — this was a lot less stressful than the previous production class. This is where I learned how powerful it is to have a group of skilled people, each in their own specific lane, where everyone can focus on their thing without worrying about other departments not pulling their weight.',
            "It was a perfect introduction to what a professional film environment should feel like. I've continued to produce films with the group of filmmakers I met here.",
        ],
    },
    {
        "slug": "forest-of-dreams",
        "title": "The Forest of Dreams",
        "category": "Short Film",
        "year": "2024",
        "role": "Cinematographer, Composer",
        "music": "all",
        "youtube_id": "VCzSAqTshd8",
        "body": [
            "My friend's senior independent study. This is the best score I've written, hands down. It's a genre that is much more in my wheelhouse, and I think it's more cohesive than any other score I've done, especially considering its length.",
            "I also think this is some of my best lighting. While chunks of the film are shot with natural lighting using a pro-mist filter for that hazy, dream effect, there is a lot of controlled lighting blended in. I'm particularly happy with the way I was able to shape the light on people's faces for some of the closeups and medium closeups.",
        ],
    },
    {
        "slug": "we-gather-here-today",
        "title": "We Gather Here Today",
        "category": "Short Film",
        "year": "2023",
        "role": "Mixer, Composer",
        "music": "all",
        "external_url": "http://cutthedeck.co/wght-film",
        "external_host": "cutthedeck.co",
        "password": "WGHT-CTD",
        "body": [
            "Despite having experience mixing and scoring bits and pieces of stuff, this is the first time I mixed and scored a short film using a professional workflow.",
            "It was shot by a couple of people from the senior capstone class, but before we took the class. Because they didn't have some important live mixing knowledge we later learned, the audio for this film was extremely messy — which made it a really good experience. I had to process almost every single clip using audio cleaning software, and I think the result is solid considering that.",
        ],
    },
    {
        "slug": "what-we-may-be",
        "title": "What We May Be",
        "category": "Short Film",
        "year": "2024",
        "role": "Composer (Final Scene)",
        "music": "some",
        "external_url": "https://mediaspace.wisc.edu/media/What+We+May+Be+2024/1_9k5wu5mt",
        "external_host": "UW Madison Mediaspace",
        "body": [
            "The other group's capstone project. All I did was score the final scene of their film, but it completely changed my perspective on scoring.",
            "Despite being a composer, I had been a score minimalist up to this point, firmly believing that a film should speak for itself without music. However, the final scene of their film wasn't really landing until we put the track I wrote under it. Suddenly, it felt powerful — not because of the track alone, but because of how it interacted with the film. The way the music accented the lead actor's performance made the ending click.",
            "Since then, I've been really interested in how score can augment a film beyond simply reinforcing something that's already there.",
        ],
    },
    {
        "slug": "trailing-off",
        "title": "Trailing Off",
        "category": "Short Film",
        "year": "2023",
        "role": "Mixer, Composer",
        "music": "all",
        "youtube_id": "dwUHoQHPtKo",
        "body": [
            "I mixed and scored this. It was, once again, shot with a suboptimal audio pipeline, so it required a decent amount of processing. However, here I got to cover up a lot of noise with natural soundscapes.",
            'The score is extremely outside of my comfort zone, with my directions being to "make it Pixar" — and I\'m quite happy with the result. I got to use a lot of woodwinds, which I rarely do otherwise.',
        ],
    },
    {
        "slug": "part-time-pursuit",
        "title": "Part-Time Pursuit",
        "category": "Short Film · Film Jam",
        "year": "2023",
        "role": "1st AC, Editor",
        "music": None,
        "youtube_id": "AS7XVRCpui0",
        "body": [
            "To mix things up, our production group did a film jam with two groups and roles drawn from a hat. I was the 1st AC and editor, two things I don't typically do on short film projects. Since it was a jam, we only had a day to shoot and a few days for post-production.",
            "With our lengthy script, we ended up doing some very run-and-gun shooting. I didn't have to pull focus on the handheld rig (thank you, Sony autofocus), so most of my work was in post. With a messy, short shoot, there are inevitably a lot of problems to think through in the edit. We were missing coverage of certain things, often had very few options to cut to, and some beats didn't fit together as scripted.",
            "Like all production challenges, this was good experience with problem-solving. If nothing else, I think it at least ended up cogent.",
        ],
    },
    {
        "slug": "zombrothers",
        "title": "Zombrothers",
        "category": "Short Film · Film Jam",
        "year": "2023",
        "role": "Composer",
        "music": "all",
        "youtube_id": "9FNyOqTV2HU",
        "body": [
            "The other group's film jam project. Once I handed off our film to be colored, mixed, and soundtrack'd, I had time to score this one.",
            "This score is a little empty on the production side of things because of the time constraint, but I'm glad to have another genre in my portfolio.",
        ],
    },
    # Com467
    {
        "slug": "oner",
        "title": "Oner",
        "category": "School · Com467 Scene",
        "year": "2023",
        "role": "Director of Photography",
        "music": None,
        "youtube_id": "b3kApIc6O0E",
        "body": [
            "The sixth and final scene from Com467. The challenge of this scene was to shoot it as an unbroken take, with a single insert allowed to stitch two takes together. It was also shot during a single class period, which was a lot less time than our previous shoots.",
            "I was the director of photography — and luckily for me, sometimes the DoP does a lot of what I liked about gaffing. I got to take another crack at lighting a scene, and here I think I was a lot more successful. We still had to use the limiting set walls, so I decided to split them and hang a curtain to make the space bigger and emulate a large window. This let us finally do the standard film thing of putting an extremely soft source of light on the far side of the actors.",
        ],
    },
    {
        "slug": "dinner-table",
        "title": "Dinner Table",
        "category": "School · Com467 Scene",
        "year": "2023",
        "role": "Gaffer",
        "music": None,
        "youtube_id": "6203e52L-vM",
        "body": [
            "The fifth scene from Com467. This was the start of something for me — I really fell in love with gaffing. I'd worked with lights before, both for this class and previous ones, but this project was the first time it was pointedly my job.",
            "Playing around with the angle and quality of light, as well as solving the puzzle of how to get lights where you need them, tickles my brain. Is this scene lit perfectly? No. Would I light it almost entirely with top lighting now? Yes — we tried but couldn't figure out how to rig it with the resources we had. Regardless, this role felt like home to me.",
        ],
    },
    {
        "slug": "studio",
        "title": "Studio",
        "category": "School · Com467 Scene",
        "year": "2023",
        "role": "Production Designer, 1st AC",
        "music": None,
        "youtube_id": "OBiQDgWPMtY",
        "body": [
            "The fourth scene from Com467 (we'll skip the third scene because it was disastrous). Here, I was the production designer and 1st AC. All of these scenes required us to build our set in the basement studios of the Commarts building.",
            "The challenge here was that it needed to be a department store, and we only had the set walls for a house or apartment. So, I used rows of clothes racks to give the space some dimension. I also worked with the actors to try to create characterful, differentiated outfits that were era-appropriate for the script (early 2000s).",
            "This is the only time I've really done production design, and building a department store in a day was a sizeable challenge. I'm glad to have had the experience. I also did the sound mix of this scene for the department showcase at the end of the semester, which is the version you see here.",
        ],
    },
    {
        "slug": "staging",
        "title": "Staging",
        "category": "School · Com467 Scene",
        "year": "2023",
        "role": "Boom Operator, Editor",
        "music": "all",
        "youtube_id": "shy-c6WqlgA",
        "body": [
            'The second scene from Com467. This project set a trend that would continue for the duration of this class, where I would try to be a "hero" and fill in for every role when things weren\'t getting done.',
            "I try not to do this nowadays because I think things run better when people have lanes they can stay in, but it felt very necessary at the time. While my assigned role was boom operator and editor, I ended up helping find and prep actors, build the set, set up the mixer, and adjust the coverage plan.",
        ],
    },
    {
        "slug": "mos",
        "title": "MOS",
        "category": "School · Com467 Scene",
        "year": "2023",
        "role": "Director",
        "music": None,
        "youtube_id": "K4end6BW2rg",
        "body": [
            "The first scene for my Advanced Cinematography and Sound Recording class (Com467), which I directed. In this class, you stick with the same group for the entire semester and rotate through roles as you shoot individual scenes from a couple of student screenplays.",
            "This was a challenging shoot. It was a week into the class, our first shoot as a group, we had just been introduced to a lot of new gear, and we were supposed to shoot this without audio and reconstruct the sound in post. While the shoot itself was brutal, it was an excellent bonding experience, and that feeling of getting through something together has become one of my favorite components of set work.",
            "Even though the final product is messy, looking back it still shows some elements of style that have stayed in my direction: POVs and long holds on nonverbal reactions.",
            'Note: This "scene" is actually two scenes that are meant to be intercut with another location, hence the cut to black after the first shot.',
        ],
    },
    # Other school work
    {
        "slug": "another-night",
        "title": "Another Night",
        "category": "School · Advanced Editing",
        "year": "2023",
        "role": "Editor",
        "music": "all",
        "youtube_id": "If1G1wlZcms",
        "body": [
            'The final project for my Advanced Editing class. We were all given the footage from a narrative short shot for the senior capstone production class during a previous year. The professor chose this film because it had an extremely messy production, and it didn\'t "work" in its intended form.',
            "Our challenge was to edit a rough cut of the film that would get around some of the narrative issues. I chose to aggressively restructure the film by making it nonlinear and cutting the entire first half — which, at the very least, made it more concise.",
        ],
    },
    {
        "slug": "narrative-short",
        "title": "Narrative Short",
        "category": "School · Intro to Media Production",
        "year": "2022",
        "role": "Cinematography, Lighting, Coordination",
        "music": "all",
        "youtube_id": "s3eNEQ9iM-I",
        "body": [
            "The final assignment from Intro to Media Production, with each group being assigned a genre of narrative to make. This was a trio assignment with a very messy and long production.",
            "The class didn't cover division of roles, so we didn't have a director, per se. I stepped up and coordinated a lot of the creative direction, but ultimately didn't understand that you have to direct actors — something quite important in narrative film, as it turns out.",
            "Despite the challenges, I think we all learned a lot of important skills that would translate to later classes and eventually professional work. Being thrown into making a narrative film without much formal guidance, you're forced to piece together a lot about lighting and cinematography, which really helps those lessons stick.",
        ],
    },
    {
        "slug": "mini-doc",
        "title": "Mini-Doc",
        "category": "School · Intro to Media Production",
        "year": "2022",
        "role": "Camera, Lights, Editor, Mixer",
        "music": "some",
        "youtube_id": "K6x0I4-AFNI",
        "body": [
            "The second assignment from Intro to Media Production. This was a duo assignment, and I handled the technical side of things — operating the camera and lights, as well as editing and mixing the final product.",
            "This was an interesting lesson in editing. With a documentary, especially something shot very quickly for a class, you just have to hope that a narrative forms from the interviews you conduct. The job of the editor is to try to assemble the best narrative you can from what you got, and while I wasn't perfectly successful on that front, it was a good low-stakes way to try my hand at it.",
        ],
    },
    {
        "slug": "1-minute-move-me",
        "title": "1-Minute Move Me",
        "category": "School · Intro to Media Production",
        "year": "2022",
        "role": "Director, Everything (Solo)",
        "music": "all",
        "youtube_id": "P8WSGyPZ998",
        "body": [
            "The first assignment from my Intro to Media Production class — the goal being to make a fake ad, PSA, or music video. This was a solo project, so I planned and executed it from the ground up (aside from acting, of course).",
            "This was my first experience with a shoot taking far longer than I expected — something you learn to calculate into your scheduling as you produce more media.",
        ],
    },
    {
        "slug": "msg2teens",
        "title": "MSG2Teens",
        "category": "School · Contest Winner",
        "year": "2017",
        "role": "Cinematography, Lighting, Post",
        "music": "all",
        "youtube_id": "KPOl8QUGsFY",
        "body": [
            "Fox47's MSG2Teens contest winner. I planned the cinematography and lighting, as well as handling all post-production work.",
            'This might be the first real group media project I worked on as a "set."',
        ],
    },
]


def music_credit_label(music):
    if music == "all":
        return "Scored all music"
    if music == "some":
        return "Scored some music"
    return None


def render_media_block(film):
    """Either an embedded YouTube iframe or a link-out card."""
    if "youtube_id" in film:
        yid = film["youtube_id"]
        return f'''    <div class="detail-media">
      <iframe
        src="https://www.youtube-nocookie.com/embed/{yid}"
        title="{html.escape(film["title"])}"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowfullscreen
        loading="lazy">
      </iframe>
    </div>'''

    # External link-out card
    pw_line = ""
    if film.get("password"):
        pw_line = f'      <p class="detail-password">Password: <code>{html.escape(film["password"])}</code></p>\n'

    return f'''    <div class="detail-media">
      <a class="detail-external" href="{html.escape(film["external_url"])}" target="_blank" rel="noopener">
        <div class="detail-external-info">
          <span class="label">Watch on</span>
          <span class="host">{html.escape(film["external_host"])}</span>
        </div>
        <span class="cta">Open ↗</span>
      </a>
{pw_line}    </div>'''


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Noah Giesler</title>
  <meta name="description" content="{desc}">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Newsreader:ital,opsz,wght@0,6..72,300..700;1,6..72,300..700&display=swap" rel="stylesheet">

  <link rel="stylesheet" href="../css/style.css">
</head>
<body>

  <header class="site-header">
    <a class="site-mark" href="../index.html">Noah Giesler</a>
    <nav class="site-nav">
      <a href="../index.html#gallery">Gallery</a>
      <a href="../index.html#films">Films</a>
      <a href="../index.html#music">Music</a>
      <a href="../index.html#contact">Contact</a>
    </nav>
  </header>

  <main class="film-detail reveal">
    <a class="back-link" href="../index.html#films">← Back to portfolio</a>

    <p class="detail-eyebrow">{category}</p>
    <h1 class="detail-title">{title}</h1>
    <p class="detail-meta">
      <span>{role}</span>
      <span>{year}</span>
{music_span}    </p>

{media}

    <div class="detail-body">
{body}
    </div>
  </main>

  <footer class="site-footer">
    <p>© <span id="year"></span> Noah Giesler. All work shown is credited to its respective productions.</p>
  </footer>

  <script src="../js/main.js"></script>
</body>
</html>
"""


def render_film_page(film, out_dir):
    music_label = music_credit_label(film.get("music"))
    music_span = f'      <span class="credit-music">{html.escape(music_label)}</span>\n' if music_label else ""

    body_html = "\n".join(
        f'      <p>{html.escape(p)}</p>' for p in film["body"]
    )

    desc = film["body"][0][:155] + ("…" if len(film["body"][0]) > 155 else "")

    page = TEMPLATE.format(
        title=html.escape(film["title"]),
        desc=html.escape(desc).replace('"', '&quot;'),
        category=html.escape(film["category"]),
        role=html.escape(film["role"]),
        year=html.escape(film["year"]),
        music_span=music_span,
        media=render_media_block(film),
        body=body_html,
    )

    out_path = Path(out_dir) / f"{film['slug']}.html"
    out_path.write_text(page, encoding="utf-8")
    return out_path


def main():
    script_dir = Path(__file__).parent
    films_dir = script_dir.parent / "films"
    films_dir.mkdir(exist_ok=True)

    for film in FILMS:
        out = render_film_page(film, films_dir)
        print(f"  wrote {out.relative_to(script_dir.parent)}")

    print(f"\nGenerated {len(FILMS)} film detail pages.")


if __name__ == "__main__":
    main()
