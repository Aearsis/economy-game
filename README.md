# Economy game

This is framework-ish application for creating real-world games involving
economy.

It is currently split into four applications:

* core -- maintaining account balances, keeping teams and entities
* recipes -- simple module that enables teams to craft (subset) using (subset)
  into another (subset of entities)
* auctions -- more complex module enabling teams to create auctions between
  teams, and also auctions between the system and team
* tokens -- simple input module based on unique code input

You may add modules as you wish, it should be simpler than writing your own
framework.

## How to make it run

First, you need to create a Python virtual environment. In the virtual
environment, install all packages required:

    pip install -r requirements

Then, you should create database:

    ./manage.py migrate

Create your superuser:

    ./manage.py createsuperuser

Then you should be able to run the server:

    ./manage.py runserver

...and make modifications in the administration, as usual in Django.

However, to run the game, you need to set few things up manually:

1. Every playing team shoud have two rows in database:
   * auth.user: usual Django user, with permission "to play a game"
   * core.player: for each user that should play the game, with team == None
   * (not) core.team: it will be created on the first login.
2. There should be a row in core.game, with filled in length, but no begin.
   Beginning the game is accomplished by clicking a button in control panel.
3. Generate some data. Currently, one-time application for generationg data
   is called "data", but it is by no means usable for any other game than
   the one we've played. It generates Entities, Tokens and Blackmarket
   auctions, and we're keeping it here just for reference.
4. Pre-generate icon sprites. After generating all entities, run
   `./manage.py shell` and `import sprites`. That will create an image with
   all needed icons and CSS file using it. This step is not necessary, but
   the app will be unusable without icons. But you can easily change
   behavior to print entity names instead.

## License

Copyright (C) 2016, Ondřej Hlavatý, Dominik Macháček, Jakub Maroušek

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

You are encouraged to publish any modification of this program, to make life
easier for more organisators of these awesome games.

## Contact and background

It's not expected to run flawlessly on any computer - there wasn't any special
effort to make it running on more than one. Whether it does or not, we'll be
very glad if you contact us and tell us what you think.

The app was made for spring camp organised by KSP (correspondence seminar of
programming) under MFF UK (Faculty of Mathematics and Physics, Charles
University in Prague). It's code original authors are (last two words are
domain in their emails):

* Hlavatý Ondřej on aearsis eideo cz
* Macháček Dominik on gldkslfmsd gmail com
* Maroušek Jakub on jakub.marousek gmail com

Contributors (icons, text content, ideas and testing):

* Pelikánová Petra on ppelikanova gmail com
* Šerý Martin martin.sery centrum cz
* Zákravská Kateřina zakravska.katerina gmail com

Preferably, contact all of us (or our successors) at ksp@mff.cuni.cz.
