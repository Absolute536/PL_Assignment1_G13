# Programming Languages Assignment 1 (Group 13)
This is the repository containing the contributions to Assignment 1.


## Precautions with the Dataset
There are some issues (?) with the dataset, which are:
- "Quantity" is recorded as floating-point values
- Random amount of whitespaces exist in the Managers' Names, like (*   Tom    Jackson  *)

So, it's better if we format/sanitise(?) the csv data after parsing it.  

For the whitespace issue, I've performed the clean-up in `base.py`, so the sanitised version is housed in `sanitised_data`.  
It should be correct, but please do double check this :P.  

For the "Quantity" issue, we can format it when filtering each record, either round it OR truncate the fractional part.  