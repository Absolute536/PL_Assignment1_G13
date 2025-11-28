# Programming Languages Assignment 1 (Group 13)
This is the repository containing the contributions to Assignment 1.

## Work Plan
Parse the dataset and answer some analytical questions such as:
1. Product category based: What is the best selling item in terms of quantity and revenue across all locations?
2. Location based: Which location is the most profitable (in terms of revenue), monthly revenue etc.
3. Manager: Who is the best performing manager (in terms of revenue)
4. Customer preferred payment method and purchase type (online or in-store)
5. Time based: Overall revenue increase or decrease over the two months? Or can be based on location as well

Each person select 1 question to work on. Everyone can provide their own implementation or build upon the template (`base.py`).    

## Precautions with the Dataset
There are some issues (?) with the dataset, which are:
- "Quantity" is recorded as floating-point values
- Random amount of whitespaces exist in the Managers' Names, like (*   Tom    Jackson  *)

So, it's better if we format/sanitise(?) the csv data after parsing it.  

For the whitespace issue, I've performed the clean-up in `base.py`, so the sanitised version is housed in `sanitised_data`.  
It should be correct, but please do double check this :P.  

~~For the "Quantity" issue, we can format it when filtering each record, either round it OR truncate the fractional part~~  
**~~(Everyone needs to use the same method to ensure consistent result).~~**   
As per the suggestion from JingYing: use the values as it is (for Quantity) to preserve accuracy

>[!NOTE]
> For assessment purposes, please refer to the source files in `src`.