"""
This file can be used to modify the picture analysis.

I recommend to first run the analysis with default settings, then look at the pdf.
If some images seem wrong you can use this file to adjust the values for them.
Then run the analysis again.

Follow the instructions above each variable (the start with a "#") to modify the program.
Never change anything but what is written after "="!

If you enter values with fractional part make sure to use "." instead of ",".

Don't forget to save the file before you run the analysis again.
"""

# Insert all IDs of Images you don't want to have in your data (comma separated)
badimages = []

# Insert the name of the substance whose concentration differs between your groups between the quotation marks below:
substance = "FBS"

# Insert the name of the cell line you are cultivating:
cells = "HEK"

# If your images contain no chamber boundaries assign the following variable "False" without quotation marks.
boundary = True

# Here you can increase the intensity of the gaussian filter for single images:
# To add a values for one image just write "increasegauss[id] = value" without quotation marks.
# Replace "id" with the image id displayed in the pdf and "value" with an integer of at least 2.
# If you want to assign the same value to a row of images copy the following without quotation marks:
"""
firstid = replace this text with the id of the first image
lastid = replace this text with the id of the last image
newgauss = raplace this text with the gauss intensity you want to assign to the row of images
for x in range(lastid-firstid):
    increasegauss[x + firstid] = newgauss
"""
# You can add multiple rows of images if you want.
increasegauss = dict()
# Add all your changes under this line:


# Here you can modify the value that is responsible for which image slices to ignore and which to keep.
# If it seems that the algorithm ignored to many slices assign a negative value.
# If it seems that the algorithm kept slices that should have been ignored assign a positive value.
# I recommend to use values between -50 and 50
# To add a values for one image just write "modifyselection[id] = value" without quotation marks.
# Replace "id" with the image id displayed in the pdf and "value" with the value you want to assign.
# Remember to use "." instead of "," when you use values with fractional part.
# If you want to assign the same value to a row of images copy the following without quotation marks:
"""
firstid = replace this text with the id of the first image
lastid = replace this text with the id of the last image
modifyer = raplace this text with the value you want to assign to the row of images
for x in range(lastid-firstid):
    modifyselection[x + firstid] = modifyer
"""
# You can add multiple rows of images if you want.
modifyselection = dict()
# Add all your changes under this line:

