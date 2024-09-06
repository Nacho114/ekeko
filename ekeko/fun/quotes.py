import cowsay
import random


def print_random_quote():
    smart_quotes = [
        "With four parameters I can fit an elephant, and with five I can make him wiggle his trunk. - Von Neumann",
        "Some strategies work in some markets some of the time - Kedar",
    ]
    wise_quotes = [
        "when an inner situation is not made conscious, it happens outside, as Fate. - C.G. Jung",
        "A fool who persists in his folly becomes wise (or rich?). - Blake",
        "There is a voice that does not use words. Listen. - Rumi",
        "Nature does not hurry, yet everything is accomplished. - Lao Tzu",
        "Silence is the language of God, all else is poor translation. - Rumi",
        "The quieter you become, the more you can hear. - Ram Dass",
        "The great way is not difficult, for those who have no preferences - HHM",
        "All we have to decide is what to do with the time that is given to us - Gandalf",
        "Sometimes the best way to solve your problems is to help someone else - Uncle Iroh",
        "Der Mensch kann zwar tun, was er will, aber er kann nicht wollen, was er will. - Shopenhauer",
        "Tat tvam asi",
        "Brahman == Atman",
        "古池や蛙飛こむ水のをと - 芭蕉",
        "Always remember that when you're pointing your finger at someone, you've got three pointing back at yourself. - Unknown",
        "You are special because of who you are - kedar",
        "In good times, be conscious of the seed that will bring about bad times. When times are bad, acknowledge the seed that will bring change. - Nacho",
        "一期一会 | one time, one meeting",
    ]
    quotes = smart_quotes + wise_quotes
    cowsay.cow(random.choice(quotes)) # type: ignore
