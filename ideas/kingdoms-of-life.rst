****************
Kingdoms of Life
****************

Overview
========
The basic idea behind this game is that players will compete with each other by
trying to direct the evolution of a handful of species. In the sense that the
game focuses on evolution, it is in the same vein as Pokemon and Spore. Unlike
those games, however, we hope that this one will involve actual evolution
rather than dressed up intelligent design.

Players will be able to direct evolution by controlling the environment, rather
than by directly controlling the species that are evolving. For example, player
can select for species that are capable of surviving various disasters by
invoking those disasters. They can also split the environment into different
regions in order to split their populations and encourage faster evolution.

Each player will begin on his own island, and players will not be able to see
or interact with any of their opponents' islands. Each island will contain
10-15 species to start with. As mentioned above, players will be able to create
mountains and rivers, as a means of dividing their species into
sub-populations. They will also be able to invoke natural disasters like
earthquakes, floods, droughts, and forest fires on their islands. All of these
actions would cost some resource (i.e. energy or god-power) that would
accumulate over time at a fixed rate.

After 15-20 minutes, all of the individual islands would come together. This
could either happen due to plate tectonics (on steroids) or the formation of an
ice bridge or something else along those lines. At this point the species
developed by all of the players would begin to compete with each other.
Furthermore, all of the players will still be able to terraform the continent
and invoke natural disasters. The player who evolved the species with the
greatest population after 10 minutes would win.

Strategy
========
There are several interesting strategic facets to this game. The first is the
trade-offs made by the player in the isolation phase of the game. Invoking more
natural disasters will initially select for more resilient species, but too
many disasters may just kill off species. It may also decrease the populations
of the species to the point where they will not be competitive in the continent
phase of the game.

In addition, different disasters will have different effects. A famine may
select for species that use little resource and reproduce slowly, while an
abundance of resource may lead to species that reproduce quickly and choke out
other species. Likewise, floods may select for aquatic species while forest
fires may select for fast ones.

The decision to create sub-populations by dividing the island is also a
trade-off. On one hand, smaller populations evolve faster because beneficial
genes can spread more rapidly. On the other hand, smaller populations are also
more vulnerable to extinction.

Because players will have to pay to affect the environment, the game will also
have a simplistic economy. This means that players will have to decide if they
want to rush (i.e. change the environment early to adapt their species) or boom
(i.e. try to make life difficult for other species in the late game).

Unanswered Questions
====================
Should all of the species in the game be able to move (i.e. be animals) or
should players be allowed to evolve plants as well? Along the same line, is
there any way to incorporate viruses or bacteria into the game?  [edit]
Implementation

Clearly, a core part of the game will be an evolution simulator. This will
require a data structure for each critter that contains tens or even hundreds
of different attributes. These attributes would determine how fit the critter
is in its particular environment. A list of potential attributes is given
below.

======================  =======================================================
Attribute               Description
======================  =======================================================
Speed   
Size    
Camouflage      
Food Source     
Hiding Instinct         
Herd Mentality          Tendency for critters to hunt in packs.
Mating pairs            Do long term partnerships form?
======================  =======================================================

The simulation would also need a way for critters to interact with each other.
Critters may interact with themselves, with a partner, or with a group
partners. Each interaction could lead to predator-prey behavior, cooperative
behavior, or anything along those lines. Interactions between members of the
same species may also lead to mating. A list of potential interactions is given
below.

======================  ==========  ===========================================
Interaction             Class       Description
======================  ==========  ===========================================
Division                Mating      Asexual reproduction. (Forever alone...)
Sex                     Mating      Same species only! Let's not get freaky!
Orgy                    Mating      An obvious generalization...
Hunting                 Eating      One critter eats another.
Foraging                Eating      Hunting critters that can't move?
Photosynthesis          Eating      Getting energy without eating anyone else.
Pack hunting            Eating      Hunting with a group of friends.
Cleaning                Symbiosis   One critter eats bugs found on another.
======================  ==========  ===========================================

A large set of things for players to do would also have to be developed. This
set would include would include things that both apply and reduce selective
pressure, and that are both cheap and expensive. For example, a flood would be
expensive and would apply a significant selective pressure. A bit of free food
would be cheap and would reduce pressure. A list of player powers is given
below.

======================  ==========  ===========================================
Power                   Cost        Description
======================  ==========  ===========================================
Flood                   $$$     
Forest Fire             $$$     
Hurricane               $$$     
Tornado                 $$$     
Volcano                 $$$     
Disease                 $$$         Diseases may be simply species, though.
Earthquake              $$$         Maybe things can evolve to earthquakes...
Monolith                $$$$$       Turns species intelligent!
Mild Weather            $$          Makes it easier for species to grow.
Inclement Weather       $$          
Create Mountain         $$$         Divide species into sub=populations.
Create River            $$      
======================  ==========  ===========================================

This game has not yet been given a name. Once this happens, a git repository
can be created. Ideas for potential names may be listed below. Naming the game
after whatever song is currently playing is not ok, although if it were we'd
have to call it "All Star"! Stupid acronyms are always encouraged!

======================  ==========  ===========================================
Title                   Acronym     Description
======================  ==========  ===========================================
Kingdoms of Life        KOL         Not funny, but I like it.
======================  ==========  ===========================================

