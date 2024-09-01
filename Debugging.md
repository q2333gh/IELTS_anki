if  write_to_card_file() accpet string.  but i use it  like this: write_to_card_file(card + "\n") . the card is an instance of AnkiCard custom class. what will happen? 


write_to_card_file(card + "\n")



(9.311698-9.26492)/10


10/0.0046778


9.26492-9.26116

turbo3.5-0125
0.000030
0.000406

gpt4o
0.011460


turbo3.5-0125 : 100 cards
4.999-4.959

0.04/100
0.0004 each card
5/0.0004 


TODO maybe try json:

{
  "input_text": "{input_text}",
  "response": {
    "sentence": "## {sentence with the word wrapped in ** **}",
    "alternatives": "{alternative1}, {alternative2}",
    "root_words_and_affixes": "{brief and comprehensively explanation of root words and affixes}",
    "definition": "{brief and accurate definition}"
  }
}
