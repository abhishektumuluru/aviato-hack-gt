# aviato-hack-gt
A customer relationship management (CRM) application using Python and IBM Watson REST calls to analyze and score the sentiment of customer complaints/feedback, pinpointing important keywords in voice conversations and emails.

>  Aviato is our solution to improving your company's customer experience effortlessly. With the help of an intelligent system powered by IBM Watson, we have paved the way to a more structured, objective, and reliable system.


##### Front-end:
The front-end was designed in Python. Using advanced audio processing, playback libraries, and speech recognition, we were able to take in user voice and convert it to text. Importantly, we made RESTful calls to IBM Watson's natural language processing API to produce a sentiment analysis based on the user's tone and word choice in a conversation.

##### Back-end:
The back-end was primarily dealt with in Node.js and Firebase. After getting the data from Watson API as JSON, it was parsed through in Node.js and after passing through our algorithm, it was pushed to a realtime database.

##### Challenges we ran into
-Integrating the API's along with the backend -Converting the data across different forms -Structuring the data in a logical manner

##### Future Plans
There's lots in store for us in the future. First of all, Aviato intends to make these databases accessible to a variety of hosts. We also wish to expand and scale our project to other large industries. Moreover, we plan to incorporate advanced data analytics into our framework and make Aviato the one stop shop for every firm's ideal consumer experience improvement service.

> All in all, the team is extremely proud of the work it has done, considering the implications this would have to thousands of companies worldwide. Stay tuned for more updates on our project.

##### Built With

- python
- node.js
- firebase
- ibm-watson
- alchemyapi
- tkinter

##### Authors
* Abhishek Tumuluru
* Mohit Chauhan
