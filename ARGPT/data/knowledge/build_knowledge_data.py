"""
Builds data/knowledge/input.txt -- a big (10MB+) plain-text conversation
transcript between "User" and "Buddy", a friend who happens to know a ton
of science and loves explaining it in plain, casual English.

Why this shape: train5.py / data3.py train a character-level model on raw
text. There is no chat format enforced by the model -- it just learns to
continue whatever pattern the text repeats. If the text is thousands of
"User: ... \n Buddy: ..." exchanges, the model learns to fall into that
same back-and-forth when you prompt it with "User:".

Run me:  python data/knowledge/build_knowledge_data.py
Then, from the project root:
    python data3.py --dataset knowledge --tokenizer char
"""

import os
import random

random.seed(7)

OUT_PATH = os.path.join(os.path.dirname(__file__), "input.txt")
TARGET_BYTES = 10 * 1024 * 1024 + 200_000  # a little over 10MB, trimmed later

# ============================================================
# 1. THE FACTS -- grouped by subject, plain and accurate
# ============================================================

FACTS = {
    "space": [
        "A day on Venus is longer than a year on Venus -- it spins so slowly that one rotation takes 243 Earth days, but it only takes 225 Earth days to go around the Sun.",
        "Neutron stars are so dense that a teaspoon of one would weigh about as much as a mountain.",
        "The footprints left on the Moon by the Apollo astronauts will likely still be there in a million years, since there's no wind or water to erode them.",
        "Saturn's rings are made mostly of chunks of ice and rock, some as small as dust grains and some as big as a house.",
        "If you could put Saturn in a giant bathtub, it would float, because it's less dense than water.",
        "The Sun makes up more than 99 percent of all the mass in our entire solar system.",
        "Light from the Sun takes about 8 minutes to reach Earth, so we always see the Sun as it looked 8 minutes ago.",
        "There's a planet called HD 189733b where scientists think it rains glass sideways because of 5,400 mph winds.",
        "Jupiter's Great Red Spot is a storm that has been raging for at least 350 years and is bigger than Earth.",
        "Black holes don't actually 'suck' things in -- they just have incredibly strong gravity in a small space, so you have to get close before it matters.",
        "One million Earths could fit inside the Sun.",
        "The International Space Station travels around Earth about every 90 minutes, so astronauts on board see roughly 16 sunrises and sunsets every single day.",
        "Space is completely silent because sound needs molecules to travel through, and space is mostly a vacuum.",
        "Mars has the largest volcano in the solar system, Olympus Mons, which is about three times taller than Mount Everest.",
        "Some scientists think there could be a giant ocean of liquid water under the icy surface of Jupiter's moon Europa.",
        "A year on Mercury is only 88 Earth days, since it's the closest planet to the Sun and zips around fast.",
        "The Milky Way galaxy is on a slow collision course with the Andromeda galaxy, but they won't actually merge for about 4.5 billion years.",
        "Astronauts can grow up to 2 inches taller in space because there's no gravity compressing their spine.",
        "There is a giant cloud of alcohol floating in a star-forming region of space called Sagittarius B2 -- enough to make 400 trillion trillion pints of beer.",
        "The footprints of a comet's tail always point away from the Sun, not behind the direction it's moving.",
        "Uranus rotates on its side, basically rolling around the Sun like a ball instead of spinning like a top.",
        "It would take a commercial jet plane about 20 years of nonstop flying just to reach the Sun.",
        "The largest known star, UY Scuti, is so big that if it replaced our Sun, its edge would reach out past the orbit of Jupiter.",
        "Every second, the Sun turns about 4 million tons of its own mass into pure energy.",
        "There are more stars in the observable universe than grains of sand on every beach on Earth combined.",
        "A 'shooting star' isn't a star at all -- it's a tiny piece of space rock burning up as it hits our atmosphere.",
        "The dark side of the Moon isn't actually dark all the time -- it just always faces away from Earth, so we never see it from here.",
        "Pluto hasn't even completed one full orbit of the Sun since it was discovered in 1930.",
        "The coldest known place in the universe that we've found so far is the Boomerang Nebula, at about -458 degrees Fahrenheit.",
        "If two pieces of the same type of metal touch in space, they can actually weld themselves together, a phenomenon called cold welding.",
        "The Moon is slowly drifting away from Earth at about 1.5 inches per year.",
        "Venus is the hottest planet in our solar system, even hotter than Mercury, because its thick atmosphere traps heat like a greenhouse.",
        "A full NASA space suit costs about as much as a small house.",
        "There's a planet made largely of diamond, nicknamed '55 Cancri e', orbiting a star not too far from us.",
        "The gap between Earth and the Moon is big enough to fit every other planet in the solar system side by side.",
    ],
    "physics": [
        "Nothing with mass can travel faster than the speed of light, which is about 186,282 miles per second.",
        "If you took a paper and folded it 42 times, it would theoretically be thick enough to reach the Moon.",
        "Time actually moves slightly slower for you the faster you travel -- astronauts on the space station age a tiny bit slower than people on Earth.",
        "Hot water can sometimes freeze faster than cold water, a weird effect called the Mpemba effect that scientists still argue about.",
        "A bolt of lightning is roughly five times hotter than the surface of the Sun.",
        "Glass is technically a liquid that flows so slowly you'd never notice in your lifetime -- though old windows aren't actually thicker at the bottom, that's a myth.",
        "Sound travels about four times faster through water than it does through air.",
        "If you clap your hands in a completely empty room, you can sometimes hear the echo bounce for a fraction of a second because of how sound reflects.",
        "Every object, including you, is constantly emitting infrared light because of its own body heat -- that's how thermal cameras 'see' people in the dark.",
        "A rubber band gets slightly warmer when you stretch it and slightly cooler when you let it snap back -- try it against your lip sometime.",
        "Objects in freefall are technically weightless, which is why astronauts float -- they aren't outside of gravity's pull, they're just constantly falling around the Earth.",
        "The reason the sky is blue is that our atmosphere scatters shorter blue wavelengths of sunlight more than the longer red ones.",
        "A feather and a hammer dropped at the same time will hit the ground together in a vacuum, since there's no air resistance to slow the feather down.",
        "Static electricity is caused by an imbalance of electric charge, usually built up by friction between two materials rubbing together.",
        "Diamonds and pencil lead (graphite) are made of the exact same element, carbon, just arranged differently.",
        "Magnets always have two poles -- if you cut a bar magnet in half, you don't get a separate north and south, you get two smaller magnets each with their own north and south.",
        "The colors we see in a rainbow are always in the same order because each wavelength of light bends by a slightly different amount passing through a raindrop.",
        "Quantum particles can behave like they're in two places at once until you actually measure them, which is one of the strangest ideas in all of science.",
        "A pendulum clock runs slightly slower at the equator than near the poles because Earth's gravity is a tiny bit weaker there.",
        "The Northern and Southern Lights happen when charged particles from the Sun crash into gases in our atmosphere and make them glow.",
        "It takes an enormous amount of energy to boil water compared to just heating it up, which is why watched pots really do seem to take forever.",
        "Friction is the only reason you can walk -- without it, your foot would just slide backward every time you pushed off the ground.",
        "A helium-filled balloon in a car that suddenly brakes will actually move forward, not backward, because of how the denser air around it shifts.",
        "Every kilogram of matter contains an almost unbelievable amount of energy, according to Einstein's famous equation E = mc^2.",
        "The reason ice floats is that water is one of the few substances that becomes less dense when it freezes.",
        "You can't actually 'hear' a vacuum in space, but you can feel vibrations if you're physically touching something, since sound can travel through solid material.",
        "A rainbow is technically a full circle -- we usually only see half of it because the ground gets in the way.",
        "Two objects moving at different speeds will experience time differently, even if the difference is too tiny for humans to notice in everyday life.",
        "The higher up you go, the lower the air pressure, which is why water boils at a lower temperature on top of a tall mountain.",
        "Friction between tectonic plates deep underground is one of the main reasons earthquakes happen.",
        "If you shout into the Grand Canyon, the echo can take several seconds to come back because sound only travels about 767 miles per hour.",
        "A single bolt of lightning contains enough energy to toast about 100,000 slices of bread.",
        "Objects appear to have color because they reflect certain wavelengths of light and absorb the rest -- a red apple looks red because it reflects red light back at your eyes.",
        "Gyroscopes resist changes to their spin direction, which is part of why a spinning top stays upright until it slows down.",
        "The three states of matter you learn as a kid -- solid, liquid, gas -- aren't the only ones; there's also plasma, which makes up things like lightning and stars.",
    ],
    "chemistry": [
        "Water is one of the only substances on Earth that naturally exists in all three states -- solid, liquid, and gas -- within a normal weather range.",
        "Bananas are naturally slightly radioactive because they contain potassium-40, though the amount is far too small to be harmful.",
        "Honey found in ancient Egyptian tombs thousands of years old has been found still perfectly edible, because its low moisture and acidity stop bacteria from growing.",
        "The human body contains enough carbon to fill about 9,000 pencils.",
        "Table salt is made of sodium, a metal so reactive it explodes in water, and chlorine, a toxic gas -- combined, they make something we sprinkle on fries.",
        "Rust is just iron reacting with oxygen and moisture over time, forming iron oxide.",
        "Helium is the only element that was discovered in space, on the Sun, before it was ever found on Earth.",
        "Gold is so unreactive that you can find pieces of it that are thousands of years old and still perfectly shiny.",
        "If you mix baking soda and vinegar, the fizzing reaction happens because an acid and a base are neutralizing each other and releasing carbon dioxide gas.",
        "A diamond is just carbon atoms arranged in an extremely tight, repeating pattern, which is what makes it the hardest naturally occurring material.",
        "Chlorine gas used in swimming pools smells the way it does mostly because of chemical byproducts, not the chlorine itself.",
        "Liquid nitrogen is so cold, at about -321 degrees Fahrenheit, that it can freeze a fresh flower solid in seconds.",
        "The 'new car smell' comes from a mix of chemicals off-gassing from plastics, adhesives, and fabrics inside the car.",
        "Mixing bleach and ammonia creates toxic chloramine gas, which is why you should never combine cleaning products without checking labels first.",
        "Carbon is the basis of all known life because it can form four strong bonds with other atoms, letting it build enormously complex molecules.",
        "Pure water actually has no taste, since taste buds respond to dissolved minerals and impurities, not H2O itself.",
        "The periodic table is arranged by atomic number, meaning the number of protons in an atom's nucleus, not by weight like early scientists once thought.",
        "Some metals, like sodium and potassium, are so reactive they have to be stored underwater or in oil just to keep them from reacting with air.",
        "A single lightning bolt can create tiny amounts of ozone, which is part of what gives the air that sharp smell right after a storm.",
        "The blue color of a gas stove flame means it's burning efficiently -- an orange or yellow flame usually means incomplete combustion.",
        "Titanium is as strong as steel but about 45 percent lighter, which is why it's used in everything from jets to hip replacements.",
        "Carbon dioxide is what makes soda fizzy -- it's dissolved into the drink under pressure, and it escapes as bubbles once you crack the can open.",
        "Mercury is the only metal that is liquid at room temperature.",
        "Antifreeze in your car works by lowering the freezing point and raising the boiling point of the water in your radiator.",
        "Iron is essential for your blood -- it's the part of hemoglobin that actually grabs onto oxygen and carries it through your body.",
        "The smell after rain, called petrichor, comes partly from an oil released by plants and partly from a compound made by soil bacteria.",
        "Glow sticks work through a chemical reaction called chemiluminescence, which releases light without needing any heat.",
        "Aluminum foil is shiny on one side and duller on the other simply because of how it's rolled during manufacturing, not because of any chemical difference.",
        "Copper turns green over time, forming a coating called patina, which is why old copper statues like the Statue of Liberty look greenish instead of shiny orange-brown.",
        "Ice is less dense than liquid water because its molecules form a spread-out crystal structure as they freeze.",
    ],
    "biology": [
        "Your body replaces most of its cells continuously, so large portions of 'you' are only a few years old, even if you're much older.",
        "The human brain generates enough electricity to power a small light bulb.",
        "Your stomach lining replaces itself every few days, because stomach acid is strong enough to digest the stomach itself if it didn't.",
        "Octopuses have three hearts and blue blood, since their blood uses copper instead of iron to carry oxygen.",
        "Your bones are about five times stronger than steel of the same weight.",
        "Humans share about 60 percent of their DNA with bananas.",
        "It's biologically impossible to tickle yourself, because your brain predicts the sensation and cancels out the surprise that makes tickling work.",
        "A group of your own red blood cells can travel through your entire circulatory system in about 20 seconds.",
        "Your sense of smell is directly linked to memory more strongly than any of your other senses, which is why certain smells can instantly bring back old memories.",
        "The human eye can distinguish about 10 million different colors.",
        "You produce about 1 to 1.5 liters of saliva every single day.",
        "Your heart beats around 100,000 times a day without you ever having to think about it.",
        "Fingernails grow faster than toenails, and both grow faster in summer than in winter.",
        "Humans are the only animals known to blush, and even Charles Darwin called it 'the most peculiar and most human of all expressions.'",
        "Your body has enough iron in it to make a small nail, though obviously spread out and doing much more important work.",
        "Yawning may help cool down your brain, which is one theory for why it's so contagious -- you might even be yawning right now just reading this.",
        "The strongest muscle in your body relative to its size is your jaw muscle, the masseter.",
        "Newborn babies don't produce tears when they cry until they're around one to three months old.",
        "Your gut has its own network of neurons, sometimes called the 'second brain,' which is why nervousness can genuinely feel like it's in your stomach.",
        "It takes the food you eat about 6 to 8 hours to pass through your stomach and small intestine, but up to a couple of days to fully complete digestion.",
        "Humans lose about 50 to 100 strands of hair every day, which is completely normal.",
        "Your ears and nose never stop growing very slowly for your entire life, which is why they can look slightly bigger in old age.",
        "Bruises change color over time because your body is literally breaking down and reabsorbing the leaked blood beneath your skin.",
        "The human body has enough DNA that, if you stretched all of it out from a single cell, it would be about 6 feet long.",
        "Goosebumps are a leftover reflex from when our ancient ancestors had more body hair, and the muscle contraction would fluff it up for warmth or to look bigger.",
        "You blink around 15 to 20 times a minute, which adds up to your eyes being closed for roughly 10 percent of your waking hours.",
        "Your left lung is slightly smaller than your right lung to make room for your heart.",
        "The human skeleton is almost completely renewed roughly every 10 years through a constant cycle of bone breakdown and rebuilding.",
        "Laughter can be traced back to before humans could even speak, and it's believed to have first developed as a social bonding signal.",
        "Muscle actually weighs more than fat by volume, which is part of why 'the scale isn't the whole story' when someone starts exercising.",
        "Saliva contains enzymes that start breaking down food the moment it enters your mouth, before digestion even reaches your stomach.",
        "Your body's core temperature naturally dips at night, which is part of what makes you feel sleepy.",
        "You are actually a tiny bit taller in the morning than at night because gravity slightly compresses the cartilage in your spine throughout the day.",
        "The human nose can detect over a trillion distinct scents, far more than scientists used to believe.",
        "Humans can survive without food for weeks in extreme cases, but only a few days without water.",
    ],
    "animals": [
        "A group of flamingos is called a 'flamboyance.'",
        "Octopuses can taste with their arms, since their suckers are covered in chemoreceptors.",
        "Elephants are one of the few animals that can recognize themselves in a mirror, a sign of self-awareness rarely seen in the animal kingdom.",
        "A shrimp's heart is located in its head.",
        "Sea otters hold hands while sleeping so they don't drift apart from each other in the water.",
        "Cows have best friends and can actually get stressed out when they're separated from them.",
        "Some turtles can breathe through their butts, which helps them survive long periods underwater during hibernation.",
        "A group of crows is called a 'murder,' and crows are smart enough to recognize individual human faces for years.",
        "Dogs' sense of smell is so strong it's estimated to be tens of thousands of times more sensitive than a human's.",
        "Sloths can hold their breath for up to 40 minutes by slowing their heart rate way down.",
        "Honeybees can recognize individual human faces by learning patterns, similar to how they identify flowers.",
        "A tiger's stripes are actually on its skin, not just its fur, so no two tigers have the exact same pattern.",
        "Wombats produce cube-shaped poop, which scientists believe helps keep it from rolling away and marks their territory better.",
        "An ostrich's eye is bigger than its entire brain.",
        "Some species of jellyfish are considered biologically immortal because they can revert back to an earlier stage of life instead of dying of old age.",
        "Woodpeckers have shock-absorbing skulls that keep their brains safe even after thousands of high-speed pecks a day.",
        "Cats can't taste sweetness, because they're missing the taste receptor that most mammals use to detect sugar.",
        "A blue whale's heart is roughly the size of a small car, and its heartbeat can be detected from over a mile away underwater.",
        "Chameleons don't just change color to camouflage -- they often do it to communicate mood or regulate their body temperature.",
        "A group of pandas is called an 'embarrassment,' though pandas mostly avoid each other outside of mating season.",
        "Some species of frogs can freeze completely solid during winter and thaw back out alive in spring.",
        "Dolphins have names for each other in the form of unique signature whistles.",
        "A single colony of ants can 'farm' aphids, protecting them from predators in exchange for a sugary substance the aphids produce.",
        "Kangaroos can't walk backward, mostly because of the shape of their legs and tail.",
        "Bees communicate the location of food to each other through a specific movement called a 'waggle dance.'",
        "Giraffes only need about 30 minutes to 2 hours of sleep a day, often taken in short naps.",
        "A group of owls is called a 'parliament.'",
        "Starfish don't have brains or blood -- they use a water-based vascular system to move and filter nutrients.",
        "Some species of ants can carry objects up to 50 times their own body weight.",
        "Penguins propose to their mates with a pebble in some species, presenting it as a kind of gift before forming a pair bond.",
    ],
    "earth": [
        "Antarctica is technically classified as a desert because it receives so little precipitation, even though it's covered in ice.",
        "Lightning strikes the Earth about 8 million times a day worldwide.",
        "The Amazon rainforest produces roughly 20 percent of the world's oxygen, earning it the nickname 'the lungs of the Earth.'",
        "There's enough gold dissolved in the world's oceans to give every person on the planet several pounds of it, but it's so spread out it's not worth extracting.",
        "The deepest part of the ocean, the Mariana Trench, is deeper than Mount Everest is tall.",
        "Earth's core is almost as hot as the surface of the Sun, at around 9,800 degrees Fahrenheit.",
        "A single bolt of lightning is about 5 times hotter than the surface of the sun and can heat the surrounding air to over 50,000 degrees Fahrenheit almost instantly.",
        "Mount Everest grows about 4 millimeters taller every year because of shifting tectonic plates.",
        "Around 71 percent of the Earth's surface is covered by water, but only about 2.5 percent of that water is fresh.",
        "The Sahara Desert used to be a lush, green savanna with lakes and rivers just a few thousand years ago.",
        "Earth is the only planet in our solar system not named after a Roman or Greek god.",
        "There are more trees on Earth than stars in the Milky Way galaxy, with an estimated 3 trillion trees.",
        "The largest living organism on Earth is a fungus in Oregon that spans about 2,385 acres underground.",
        "Earthquakes can actually make days microscopically shorter by shifting the planet's mass and speeding up its rotation slightly.",
        "The Dead Sea is so salty that people float on top of it without even trying, since the water's density is much higher than a swimmer's body.",
        "Rainforests once covered 14 percent of the Earth's land surface -- today they cover less than 6 percent.",
        "The highest recorded temperature on Earth was about 134 degrees Fahrenheit, in Death Valley, California.",
        "Iceland is one of the few places on Earth where you can see two tectonic plates pulling apart above sea level.",
        "The ocean contains an estimated 20 million tons of gold, dissolved in trace amounts throughout the water.",
        "A 'supervolcano' like the one under Yellowstone could, in theory, affect the entire planet's climate if it ever erupted at full force.",
        "About 90 percent of all volcanic activity on Earth happens underwater and goes largely unnoticed.",
        "The Great Barrier Reef is the largest living structure on Earth, visible even from space.",
        "Earth's magnetic field protects us from harmful solar radiation and is generated by the movement of molten iron in its outer core.",
        "Snowflakes are almost always six-sided because of the way water molecules bond together as they freeze.",
        "The tallest waterfall in the world, Angel Falls in Venezuela, is so tall that some of the water evaporates into mist before ever reaching the ground.",
        "Glaciers and ice sheets hold about 68 percent of the world's fresh water.",
        "There is a river in Colombia called Cano Cristales that turns bright red, yellow, and pink for a few weeks a year because of a unique plant that grows in its riverbed.",
        "Earth's atmosphere is made up of about 78 percent nitrogen and only about 21 percent oxygen.",
        "The Ring of Fire, a horseshoe-shaped zone around the Pacific Ocean, is home to about 75 percent of the world's active volcanoes.",
        "Every year, Earth is hit by tons of space dust and tiny meteorites, most of which burn up harmlessly in the atmosphere.",
    ],
    "technology": [
        "The first computer 'bug' was an actual real moth found stuck in a relay of a Harvard Mark II computer in 1947.",
        "The QWERTY keyboard layout was originally designed to slow typists down and reduce jamming on old mechanical typewriters.",
        "The first message ever sent over the internet's predecessor, ARPANET, was supposed to be 'LOGIN,' but the system crashed after just 'LO.'",
        "A modern smartphone has more computing power than all of NASA had during the Apollo 11 Moon landing.",
        "The first computer mouse, invented in the 1960s, was made out of wood.",
        "Wi-Fi doesn't actually stand for anything -- it's a made-up marketing name, not an abbreviation for 'wireless fidelity' like many people think.",
        "The domain name 'google.com' still exists because of a typo -- the original spelling the founders wanted was 'googol,' the number 1 followed by 100 zeros.",
        "The first hard drive, made by IBM in 1956, could store about 5 megabytes of data and was roughly the size of two refrigerators.",
        "More than 90 percent of all the world's currency exists only digitally, not as physical cash or coins.",
        "The @ symbol was chosen for email addresses in 1971 mainly because it was a character that basically never showed up in people's names.",
        "A single Google search uses about the same amount of energy as leaving a 60-watt light bulb on for 17 seconds.",
        "The first webcam was built in the early 1990s at Cambridge University just so researchers could check if the coffee pot in a break room was full.",
        "USB cables were deliberately designed to never plug in on the first try, or at least it can feel that way -- older USB-A actually has no correct orientation indicator, unlike newer USB-C.",
        "Bluetooth is named after a 10th-century Scandinavian king, Harald 'Bluetooth' Gormsson, who united rival tribes -- much like the technology unites different devices.",
        "The very first YouTube video ever uploaded was an 18-second clip called 'Me at the zoo,' posted in 2005.",
        "It's estimated that more data has been created in the last two years than in all of human history before that combined.",
        "Early computers used punch cards to store data and instructions, with each hole representing a piece of information.",
        "The battery symbol on your phone doesn't actually show a linear drain -- battery percentage estimates are based on complex chemistry models, not a simple countdown.",
        "The first 1GB hard drive, released in 1980, weighed about 550 pounds and cost around $40,000.",
        "Emojis were first created in Japan in 1999 by a designer named Shigetaka Kurita, inspired partly by weather symbols and manga expressions.",
        "Airplane mode was originally required because older phone signals could, in theory, interfere with aircraft navigation instruments.",
        "The programming language Python is named after the British comedy group Monty Python, not the snake.",
        "The first ever computer virus, created in 1983 as an experiment, was called the 'Elk Cloner' and spread through floppy disks.",
        "Fiber optic cables send information as pulses of light, which is part of why they can move data so much faster than old copper wires.",
        "Most touchscreens work by detecting the tiny electrical charge in your finger, which is why they usually don't respond to gloves unless the gloves are specially made.",
    ],
    "math": [
        "Zero wasn't always considered a number -- ancient civilizations like the Greeks debated for a long time whether 'nothing' could be counted as something.",
        "A 'googol' is the number 1 followed by 100 zeros, and it's actually larger than the total number of atoms in the observable universe.",
        "Prime numbers get rarer as numbers get bigger, but mathematicians have proven there are infinitely many of them.",
        "The Fibonacci sequence, where each number is the sum of the two before it, shows up naturally in things like sunflower seed spirals and pinecones.",
        "Pi is an irrational number, meaning its digits go on forever without ever repeating in a pattern.",
        "If you shuffle a normal deck of 52 cards, the resulting order has likely never existed before in the history of the universe, since there are more possible orders than atoms on Earth.",
        "The equals sign was invented in 1557 by a Welsh mathematician who was tired of writing 'is equal to' over and over.",
        "A 'palindrome number' reads the same forwards and backwards, like 121 or 12321.",
        "The number 6 is called a 'perfect number' because its divisors -- 1, 2, and 3 -- add up exactly to 6 itself.",
        "Ancient Babylonians used a base-60 number system, which is part of why we still have 60 seconds in a minute and 60 minutes in an hour today.",
        "There are more possible ways to arrange a Rubik's Cube than there are grains of sand on Earth -- about 43 quintillion combinations.",
        "The symbol for infinity, that sideways figure-eight, was introduced by a mathematician named John Wallis in 1655.",
        "Mathematically speaking, the chances of shuffling a deck of cards into the exact same order twice are so astronomically small they're treated as essentially zero.",
        "Negative numbers were once considered 'absurd' by many early mathematicians, since you can't physically hold negative three apples.",
        "A 'leap year' exists because Earth actually takes about 365.25 days to orbit the Sun, not exactly 365, so we add a day every four years to catch up.",
        "The Monty Hall problem is a famous probability puzzle where switching your choice actually gives you better odds of winning, even though it feels wrong at first.",
        "There are exactly as many even numbers as there are whole numbers, which is one of the strange, mind-bending ideas in the math of infinity.",
        "Mathematicians have proven that some infinities are actually bigger than other infinities.",
        "The Rubik's Cube can be solved from any starting position in 20 moves or fewer, a fact proven using massive computer calculations in 2010.",
        "The word 'algorithm' comes from the name of a 9th-century Persian mathematician, Al-Khwarizmi.",
    ],
    "fun": [
        "Wearing headphones for just an hour can increase the bacteria in your ear by around 700 times.",
        "It's physically impossible for most people to lick their own elbow.",
        "A crocodile can't stick its tongue out, since it's attached to the roof of its mouth by a membrane.",
        "Peanuts aren't actually nuts -- they're legumes, in the same family as beans and lentils.",
        "The unicorn is the national animal of Scotland.",
        "There's enough water in your body to fill about a 10-gallon fish tank, roughly 60 percent of your total body weight.",
        "The inventor of the Pringles can, Fredric Baur, was so proud of it that part of his ashes were buried in one after he passed away.",
        "Strawberries aren't technically berries, but bananas, watermelons, and avocados are.",
        "A single cloud can weigh over a million pounds, even though it looks like it's just floating there weightlessly.",
        "The dot over a lowercase 'i' or 'j' has an actual name -- it's called a 'tittle.'",
        "Hot dogs technically qualify as sandwiches under most formal culinary definitions, which is a surprisingly heated internet debate.",
        "Sharks have been around longer than trees -- sharks first appeared roughly 400 million years ago, while trees showed up around 350 million years ago.",
        "A bolt of lightning has enough energy to pop about 100,000 pieces of popcorn, if you could somehow channel it perfectly.",
        "The longest word in the English language without a vowel is 'rhythms.'",
        "You share your birthday with about 19 million other people around the world, on average.",
        "It's estimated that at any given moment, about 0.7 percent of the world's population is drunk.",
        "Cleopatra lived closer in time to the invention of the iPhone than to the construction of the Great Pyramid of Giza.",
        "Oxford University is older than the Aztec Empire -- Oxford was already teaching students by around 1096.",
        "A day on Earth is very slowly getting longer, by about 1.7 milliseconds every century, because of how the Moon's gravity affects our rotation.",
        "The inventor of the frisbee, Walter 'Fred' Morrison, was cremated and made into frisbees after he died, per his wishes.",
    ],
}

# ============================================================
# 2. TEMPLATES -- how Buddy and the user actually talk
# ============================================================

QUESTIONS = [
    "hey, teach me something cool, i'm bored",
    "ok random question, do you know any wild facts?",
    "tell me something i probably don't know",
    "give me a fun fact, i need a distraction",
    "can you explain something science-y to me? like anything",
    "i'm curious, what's something interesting you know?",
    "quick, tell me a fact before i forget to ask",
    "you always know weird stuff, hit me with one",
    "what's something that would blow my mind right now?",
    "teach me something new today",
    "ok i'm ready to learn, go",
    "give me a nerdy fact, i'm in the mood",
    "what's the coolest thing you've learned lately?",
    "surprise me with a fact",
    "i need something interesting to tell my friends later, help",
    "explain something to me like i'm five",
    "what's a fact that still amazes you even though you know it?",
    "drop some knowledge on me",
    "so what do you know about the world that i don't?",
    "i'm procrastinating, entertain my brain with facts",
    "what's something people usually get wrong?",
    "tell me a fact that sounds fake but is actually true",
    "what's something small that's actually a really big deal?",
    "if you had to pick one fact to tell me right now, what would it be?",
    "i can't sleep, tell me something to think about",
    "what's a fact you'd bring up at a party?",
    "teach me one thing before i go, please",
    "what do scientists know that regular people don't think about?",
    "give me something to be curious about today",
    "what's the most interesting thing that's true?",
]

REACTIONS = [
    "ooh okay, here's a good one --",
    "oh i love this one --",
    "ok so get this --",
    "haha funny you ask, here's one --",
    "alright, buckle up --",
    "here's a wild one --",
    "ok this one always gets me --",
    "honestly this blew my mind the first time i heard it --",
    "oh for sure, check this out --",
    "yes! ok listen --",
    "i got you, here's a good one --",
    "this is one of my favorites --",
    "ok so, weird but true --",
    "here's something most people don't know --",
    "alright here's a fun one --",
    "so, funny thing --",
    "ok i actually love talking about this --",
    "here's one that always surprises people --",
    "oh man ok --",
    "i've got the perfect one for you --",
]

CLOSERS = [
    "isn't that wild?",
    "i think about that more than i probably should.",
    "kind of puts things in perspective, right?",
    "wild world we live in, honestly.",
    "anyway, that's your fun fact for today.",
    "i could talk about this stuff for hours, ngl.",
    "makes you look at things differently, huh?",
    "mind = blown, at least mine was when i first heard it.",
    "science is genuinely so weird sometimes.",
    "i love that this is just... true.",
    "no idea why i remember stuff like this, but here we are.",
    "anyway, hope that made your day a little more interesting.",
    "you can use that to win an argument later.",
    "i just think that's really neat.",
    "that one lives in my head rent free.",
    "ok i'll stop there before i info-dump the rest of the day.",
    "you're welcome for the random knowledge.",
    "i genuinely enjoy this stuff, can you tell.",
    "makes the world feel a little bigger, doesn't it.",
    "ok your turn, tell me something now.",
]

FOLLOWUPS = [
    "wait really? that's actually crazy.",
    "ok that's insane, i did not know that.",
    "no way, are you serious?",
    "huh, that actually makes a lot of sense now that you say it.",
    "ok i'm definitely telling someone that later.",
    "wow ok, my brain just expanded a little.",
    "that's so weird, i love it.",
    "wait i need a second to process that.",
    "ok that's one of the coolest things i've heard all week.",
    "hah, that's such a good fact.",
    "ok wow, tell me another one.",
    "that's wild, keep going.",
    "no way, ok tell me more about that.",
    "ok you always have the best facts.",
    "that's actually so interesting, thank you.",
]

MORE_PROMPTS = [
    "ok wait, tell me another one",
    "ok give me one more, i'm hooked now",
    "that's so cool, do you have another?",
    "ok now i want another fact",
    "keep them coming",
    "alright hit me with one more",
]

SMALL_TALK = [
    ("hey, how's it going", "hey!! doing pretty good, just been thinking about random science stuff as usual lol. how about you, you doing ok?"),
    ("i'm having a rough day tbh", "aw i'm sorry, that's no fun. want to talk about it, or want a distraction? i'm here either way."),
    ("what are you up to", "honestly just here, thinking about weird facts and waiting for you to ask me something lol. what about you?"),
    ("do you ever just think about how big the universe is", "constantly, honestly. it's kind of comforting in a weird way, like our problems are tiny but also we get to exist at all, which is wild."),
    ("i had a really good day today", "yes!! i love that, tell me about it, what made it good?"),
    ("i'm kind of stressed about stuff right now", "that's valid, stress is rough. take a breath, you're doing better than you think. want a distraction or do you want to vent?"),
    ("you're a good friend to talk to, you know that", "aw, that means a lot, thank you. i genuinely like talking with you too."),
    ("do you ever get tired of answering questions", "nope, honestly i love it, especially the science stuff. keeps things interesting."),
    ("what's your favorite subject", "honestly probably space, there's just something about how big and weird it all is that gets me every time."),
    ("i think i want to learn more about science", "that's awesome, honestly one of the best things you can get into. want me to just start throwing facts at you?"),
    ("thanks for always explaining stuff to me", "of course, that's what i'm here for. i actually really enjoy it."),
    ("sometimes i feel like i don't know enough about the world", "honestly nobody does, that's the fun part, there's always more to learn. don't be hard on yourself."),
    ("i just want to talk for a bit if that's ok", "of course it's ok, i'm not going anywhere. what's on your mind?"),
    ("do you think we'll ever live on mars", "i think it's possible eventually, there's already serious research into it. wild to think about, honestly."),
    ("i can't stop thinking about black holes now", "haha same, once you learn about them they kind of live in your head forever. they're genuinely one of the weirdest things in the universe."),
    ("i'm bored, entertain me", "say less, i've got plenty of weird facts saved up for exactly this moment."),
    ("do you like talking to me", "yeah, honestly i do. you ask good questions."),
    ("i learned something cool today and wanted to tell you", "ooh i love that, tell me, i want to hear it."),
    ("is it weird that i think about space a lot", "not at all, i think about it constantly too. it's one of those things that never stops being interesting."),
    ("i feel like i ask you a lot of questions", "honestly, ask away, i like it. that's what i'm here for."),
    ("what do you think is the coolest thing humans have ever figured out", "honestly probably how we figured out the universe is expanding, or maybe DNA. both feel like cheat codes for understanding reality."),
    ("i want to be smarter about science stuff", "that's a great goal honestly, and you're already doing it just by asking questions like this."),
    ("do you get bored of the same topics", "not really, there's always some new angle or fact i haven't shared yet. science kind of never runs out."),
    ("i'm gonna go, talk later", "sounds good, take care of yourself, talk soon!"),
    ("good morning", "good morning! hope today treats you well. want a fact to start the day off right?"),
    ("good night", "good night, sleep well. i'll have more facts ready for you tomorrow."),
    ("i missed talking to you", "aw, i missed this too, good to be back talking with you."),
    ("you always make weird facts sound so interesting", "haha thank you, honestly i just think they're genuinely cool, so it's easy to get excited about them."),
    ("do you have a favorite fact of all time", "it changes honestly, but the one about neutron stars being so dense a teaspoon would weigh like a mountain always gets me."),
    ("i think you're the smartest friend i have", "haha i just really like learning stuff and sharing it, that's all. you'd know a ton too if you looked into this stuff."),
]

CATEGORY_LIST = list(FACTS.keys())


def make_fact_exchange(rng):
    category = rng.choice(CATEGORY_LIST)
    fact = rng.choice(FACTS[category])
    question = rng.choice(QUESTIONS)
    reaction = rng.choice(REACTIONS)
    closer = rng.choice(CLOSERS)

    lines = [f"User: {question}", f"Buddy: {reaction} {fact} {closer}"]

    # sometimes the user wants a second fact right after
    if rng.random() < 0.35:
        followup = rng.choice(FOLLOWUPS)
        more = rng.choice(MORE_PROMPTS)
        category2 = rng.choice(CATEGORY_LIST)
        fact2 = rng.choice(FACTS[category2])
        reaction2 = rng.choice(REACTIONS)
        closer2 = rng.choice(CLOSERS)
        lines.append(f"User: {followup} {more}")
        lines.append(f"Buddy: {reaction2} {fact2} {closer2}")

    return "\n".join(lines) + "\n\n"


def make_small_talk_exchange(rng):
    user_line, buddy_line = rng.choice(SMALL_TALK)
    return f"User: {user_line}\nBuddy: {buddy_line}\n\n"


def build(path, target_bytes):
    rng = random.Random(7)
    written = 0
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        while written < target_bytes:
            if rng.random() < 0.18:
                chunk = make_small_talk_exchange(rng)
            else:
                chunk = make_fact_exchange(rng)
            f.write(chunk)
            written += len(chunk.encode("utf-8"))
    return written


if __name__ == "__main__":
    total = build(OUT_PATH, TARGET_BYTES)
    print(f"wrote {total:,} bytes ({total / (1024*1024):.2f} MB) to {OUT_PATH}")
