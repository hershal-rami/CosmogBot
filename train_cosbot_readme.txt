Hello and welcome to the training process for Cosmog Bot Draft Helper! 

This document will explain two major things in this order: 
What are the goals for Cosmog Your Drafting Friend?
And how does this whole training process work?


1: What are the goals for Cosmog Draft?
Have you ever found yourself in this situation? You've drafted a nice core with a couple of mons and then you look at the draft board and say "Oh no!"
I dont know what else to draft to round this out!
Or you're trying to get your friend into draft and you know they can battle but they draft the most horrendous abomination you've ever seen? (show my earlier drafts here)
Well, hopefully Cosmog can help you with that.
My vision for this bot is that you can supply it with the current pokemon on your team and it will analyze every pokemon available and rank them, so you can see which pokemon best fit in your team.
You can even supply it with filters, so it will only look over pokemon that know stealth rock, or electric types, or pokemon below a certain point value in case you're looking for something specific.
It can also help when you get sniped!
Hopefully this will take some of the stress out of drafting for many players!

The only problem is we need to get the model to actually understand what pokemon are better in what situations....
That's where this program comes in! To help a machine learning model understand which pokemon are better for a specific team.

2: How does this training process work?
After reading this document you can run train_cosbot.py to begin generating training data.
The code will give you a randonmly generated team that you are to assume is what you have drafted so far. In the form of:

-------------------------------------------------------------------------------------
| Name               | HP  | ATK | DEF | SPA | SPD | SPE | TYPE1      | TYPE2       |
-------------------------------------------------------------------------------------
| Gengar             | 60  | 65  | 60  | 130 | 75  | 110 | Ghost      | Poison      |
-------------------------------------------------------------------------------------
| Mr. Mime-Galar     | 50  | 65  | 65  | 90  | 90  | 100 | Ice        | Psychic     |
-------------------------------------------------------------------------------------
| Basculegion        | 120 | 112 | 65  | 80  | 75  | 78  | Water      | Ghost       |
-------------------------------------------------------------------------------------
| Forretress         | 75  | 90  | 140 | 60  | 60  | 40  | Bug        | Steel       |
-------------------------------------------------------------------------------------
| Mesprit            | 80  | 105 | 105 | 105 | 105 | 80  | Psychic    | None        |
-------------------------------------------------------------------------------------

It will also give you a summary of various features about the team in the form of:

=====================================================================================
                                      FEATURES
=====================================================================================
Difference between average ATK and SPATK: 5.599999999999994
Difference between average DEF and SPDEF: 6.0
Average Speed Stat: 81.6
Severity of weaknesses: 26.0
Number of Types you don't have at least 2 resistances for: 9
Number of Types you have at least 2 unresisted weaknesses for: 8
Number of repeated types (over 2): 0
Utility moves: ['Toxic Spikes', 'Haze', 'Clear Smog', 'Will-o-Wisp', 'Rapid Spin', 'Reflect', 'Light Screen', 'Stealth Rock', 'Spikes']

This is what the model will actually see when it is trying to differentiate which pokemon is better.
A detailed description of these features is listed below.
This is supposed to be a set of things that a human would consider when thinking about adding a pokemon to a team.
This is not an exhaustive list so if you are going through some examples and think of something that you usually think about when teambuilding, please let us know!
Reach out to Casey over discord and tell him your ideas. All are welcome! That is also a part of the training process is finding better ways to characterize teams.

But back to the problem at hand now that you have seen your given draft team, them model wil present you with two candidate pokemon.
You will then be asked to state which pokemon is better to add to the team.
It is important that you think of which is better to add to the team and not which is better in general.
The better pokemon may be better to add to the team but the better pokemon may also make some of the teams weaknesses more pronounced.
You should also think of this pokemon as the last pokemon you will add to the team, even if the team would only have 3 mons you want to maximize the potential team with just this pokemon only.

The output of the two candidate pokemon will look like this:

*********************
     NEW POKEMON
*********************
-------------------------------------------------------------------------------------
| Name               | HP  | ATK | DEF | SPA | SPD | SPE | TYPE1      | TYPE2       |
-------------------------------------------------------------------------------------
| Pokemon 0          | 105 | 140 | 95  | 55  | 65  | 45  | Fighting   | None        |
-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------
| Pokemon 1          | 105 | 170 | 95  | 55  | 65  | 15  | Water      | None        |
-------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------

=====================================================================================
                FEATURES WITH ADDING POKEMON 0
=====================================================================================
Difference between average ATK and SPATK: 9.5
Difference between average DEF and SPDEF: 10.0
Average Speed Stat: 75.5
Severity of weaknesses: 26.0
Number of Types you don't have at least 2 resistances for: 9
Number of Types you have at least 2 unresisted weaknesses for: 7
Number of repeated types (over 2): 0
Utility moves: ['Defog']
-------------------------------------------------------------------------------------

=====================================================================================
                FEATURES WITH ADDING POKEMON 1
=====================================================================================
Difference between average ATK and SPATK: 14.5
Difference between average DEF and SPDEF: 10.0
Average Speed Stat: 70.5
Severity of weaknesses: 26.0
Number of Types you don't have at least 2 resistances for: 7
Number of Types you have at least 2 unresisted weaknesses for: 8
Number of repeated types (over 2): 0
Utility moves: []

With the features being output, taking the whole team into account as if this pokemon was added.
So the features for pokemon 0 are as if you have 6 pokemon in the team now the original 5, and the new 6th pokemon, pokemon 0.
The same is true for pokemon 1.
You will them be asked to enter whick pokemon is better 0 or 1.
Please only type the number then press enter.
You may also enter option 2 if there is no real difference or the pokemon is nonsensical.
Use this option sparingly. Use it only if there is truly no difference between the two pokemon, no features that stand out.
Or if the pokemon is nonsensiscal, negative values in a stat or something of the like.

You can then press enter to continue generating data or type done then press enter to stop for now.
You can safely do a couple then resume at any time, the program saves after every example.

After you have completed training please send Casey your Training_data.json file either over discord or email at casey.hanks.2020@gmail.com and please let him know your thoughts on the whole thing.
