### To develop and implement

Multiple images in a post 
- [ ] carousel - only limited to 3 images, and need to make it longer (any length)
- [ ] image size control required in post-detail page
- [ ] currently image1 is required / in view, this might be improved
- [ ] if there is only 1 image, disable carousel / implement this in view
- [ ] currently only image1 is shown in post-list-view in a card (i.e., implement carousel in post-list-view as well)
- [ ] in post create form, make that once an image be uploaded (after validation), another image field appear (may use javascript, but may need to disassemble the crispy form thing)

Authentication 
- [ ] Private posts and cards have to be only exposed to the owner / access through urls have to be blocked

Main page 
- [ ] if not logged in, main page has to show a basic instruction how to use IssueTracker (with animated screen), public cards have to be shown
- [ ] if logged in, main page has to show private cards and public cards 

Card arrangement
- [ ] Private/public cards have to be in accordian (bootstrap)
- [ ] Private/public cards might be grouped into menu/nav
- [ ] private cards -> mycards

Card movements
- [ ] may implement Apple-Album style (or much simpler) card movements using CSS/JS