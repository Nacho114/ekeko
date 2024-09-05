import cowsay
import random


def print_random_quote():
    quotes = [
        "when an inner situation is not made conscious, it happens outside, as Fate. - CJ",
        "A fool who persists in his folly becomes wise (or rich?). - Blake",
        "There is a voice that does not use words. Listen. - Rumi",
        "There is always something trending",
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
    ]
    cowsay.cow(random.choice(quotes))
