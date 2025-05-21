Business Objective
To build an assessment tool that our HR team can use to conduct initial assessment of all candidates, score them and maintain those scores corresponding to each user in a database for future audit purpose.
Process Scope
1.
The current scope covers creation of specialization, questions, corresponding options for each question along with correct answer, scoring mechanism, and assessments.
2.
Specialization aspect covers the type of questions and how responses need to be collected, for example for aptitude, there will be one question, 4-5 options and one correct answer. But for reading comprehension type of questions, there will be a paragraph then questions and corresponding options.
3.
The current scope also covers assigning users using their email addresses so that they can receive the assessment link
Actors
There will 3 roles define in the system –
1.
Admin – who can setup the specializations, questions, scoring mechanism, get reports and all setup related activities
2.
Talent lead – Who can create an assessment templates and select what all questions should be there in that assessment, upload user emails, review scores
3.
User – who will receive a link in their email for assessment and will land on the interface using the link and completes the assessment
Feature Scope
Setup
1.
As an admin I should be able to create assessment templates by assigning a unique name. Under each assessment template I should be able to create questions and assign a specialization(type) for each question. The specializations and their corresponding response handling mechanism are defined as follows –
a.
Aptitude – this type of question will have 5 options defined and only one among them will be correct.
b.
Reading comprehension – This type should ask the user to first add a paragraph and then in next step add questions and options linked to each paragraph.
c.
Typing – This type should ask the user to just enter the paragraph. When these type of questions are displayed to user, the para should be divided into individual lines and
under each line, a response field should be displayed. User will retype each line in these response fields that can allow to assess the typing speed, accuracy of the user
2.
As an admin user, I should be able to define test assessment and test users to assess the average time taken to complete each assessment
3.
As an admin user, I should be able to setup a percentage for each assessment template so that out of all defined questions, the number of questions meeting the defined percentage will be randomly picked up and displayed to user
Publish assessment
1.
As a talent lead I should be able to select an assessment template, add user emails and publish the assessment. The system should create a custom link for the interface an send it to all mentioned email ids.
Take assessment
1.
As an user, I should be able to click on the link received and land on the login page of the interface. I should be able to enter email address as verification and upon successful verification, I will land on the assessment page
2.
As an user, I should have the option to start the assessment and all the selected questions that are part of the assessment template should be displayed one after another along with define options
3.
Each selection done by user must be saved and should be scored based on the correct answer defined in the system
View Scores
1.
As a talent lead, I should be able to get an assessment complete report at the end of each assessment and it should display the list of users in first column and total score in second column and form the next column it can show the question displayed and response provided and so on