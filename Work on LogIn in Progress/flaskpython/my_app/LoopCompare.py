# Function to check for repeated phrases
def check_repeated_phrases(password):
  for i in range(3):
    phrase_counts = {}

    for phrase in list:
        if phrase in phrase_counts:
            phrase_counts[phrase] += 1
        else:
            phrase_counts[phrase] = 1

    repeated_phrases = [phrase for phrase, count in phrase_counts.items() if count > 1]
    return repeated_phrases
  print("password has fufilled the requirement of not having excessive repeated phrases")
if  phrase_counts > 3:
  print(("Please create a different password as")+password+("should not have too many repeating phrases"))
else:
  phrase_counts +=1
return
