from django.apps import AppConfig
from django.db.models.signals import post_migrate
import os

def populate_default_data(sender, **kwargs):
    from django.contrib.auth.models import User   # moved inside function
    from myapp.models import Users, Events         # moved inside function

    # Create users
    users_created = 0
    if not Users.objects.exists():
        default_users = [
            {"username": "dvc_superuser@insite.4cd.edu", "DVC_ID": "0000001", "role": "superuser", "first_name": "Superuser"},
            {"username": "andrew@insite.4cd.edu", "DVC_ID": "0000002", "role": "admin", "first_name": "Andrew"},
            {"username": "frank@insite.4cd.edu", "DVC_ID": "0000003", "role": "admin", "first_name": "Frank"},
            {"username": "heidi@insite.4cd.edu", "DVC_ID": "0000004", "role": "admin", "first_name": "Heidi"},
            {"username": "hoang@insite.4cd.edu", "DVC_ID": "0000005", "role": "admin", "first_name": "Hoang"},
            {"username": "kayla@insite.4cd.edu", "DVC_ID": "0000006", "role": "admin", "first_name": "Kayla"},
            {"username": "seokyoung@insite.4cd.edu", "DVC_ID": "0000007", "role": "admin", "first_name": "Seokyoung"},
            {"username": "dvc_user@insite.4cd.edu", "DVC_ID": "0000008", "role": "user", "first_name": "User"}
        ]

        for u in default_users:
            user_obj = User.objects.create_user(username=u["username"], password="password", first_name=u.get("first_name", "User"))
            Users.objects.create(user=user_obj, DVC_ID=u["DVC_ID"], role=u["role"])
            users_created += 1
        print(f"Created {users_created} default users.")

    # Create events
    events_created = 0
    if Events.objects.exists():
        print("Events already exist. Skipping event creation.")
    else:
        author = Users.objects.first()  # default DVC user as author

        event_data = [
            # Dec 01
            {
                "name": "Distance Education & Digital Equity Committee",
                "date": "2025-12-01",
                "start_time": "12:30 PM",
                "end_time": "2:00 PM",
                "location": "Administration Building - AB | 217",
                "building_code": "VR",
                "campus": "Virtual",
                "description": """
        <p>The Distance Education & Digital Equity (DEDE) Committee is charged with reviewing, creating, and recommending policies, procedures, and practices to the Faculty Senate in order to promote strategic, high-quality, and sustainable growth and delivery of distance education at DVC that fosters academic excellence, equity, and student success.</p>
        <p>Meeting Agendas & Minutes on BoardDocs</p>
        <p><a href='https://go.boarddocs.com/ca/ccccd/Board.nsf/goto?open=&id=AVB4547655EB'>https://go.boarddocs.com/ca/ccccd/Board.nsf/goto?open=&id=AVB4547655EB</a></p>
        """,
                "event_type": "",
                "image_filename": "1.jpg",
            },
            {
                "name": "Curriculum Committee Meeting",
                "date": "2025-12-01",
                "start_time": "2:30 PM",
                "end_time": "4:30 PM",
                "location": "Community Conference Center - CCC",
                "building_code": "VR",
                "campus": "Virtual",
                "description": """
        <p>The Curriculum Committee oversees the college curriculum and makes recommendations to the Vice President of Instruction regarding new courses and programs, degree, certificate and transfer requirements including General Education requirements, and other matters which concern curriculum.</p>
        <p>Meeting Agendas & Minutes on BoardDocs</p>
        <p><a href='https://go.boarddocs.com/ca/ccccd/Board.nsf/goto?open=&id=D7VQF968FEF0'>https://go.boarddocs.com/ca/ccccd/Board.nsf/goto?open=&id=D7VQF968FEF0</a></p>
        """,
                "event_type": "",
                "image_filename": "2.jpg",
            },

            # Dec 02
            {
                "name": "Art Department Holiday Art Sale",
                "date": "2025-12-02",
                "start_time": "9:00 AM",
                "end_time": "3:00 PM",
                "location": "Art Complex - A | 101",
                "building_code": "A",
                "campus": "Pleasant Hill",
                "description": """
        <p><strong><em>All proceeds benefit the photography, printmaking and ceramic areas.</em></strong></p>
        <p>Discover one-of-a-kind ceramics, prints, and photographs, each piece born in our classrooms and crafted by the hands of DVC's talented artists – our faculty, students, and staff.</p>
        <p>This is more than a sale; it's a chance to own a piece of our creative journey and directly support the next generation of artists.</p>
        """,
                "event_type": "",
                "image_filename": "3.jpg",
            },
            {
                "name": "Business Beyond the Classroom - Scholarships & DVC Alumni Association",
                "date": "2025-12-02",
                "start_time": "1:00 PM",
                "end_time": "3:00 PM",
                "location": "Business and World Language - BWL | 109",
                "building_code": "VR",
                "campus": "Virtual",
                "description": """
        <p>Attend this workshop to learn about the DVC Foundation - your source for scholarships, alumni association benefits, and more!</p>
        <p>Explore real-world business and entrepreneurship practices, build meaningful connections, and discover pathways to advance your education and career. No experience required—just bring your curiosity and goals!</p>
        """,
                "event_type": "",
                "image_filename": "4.jpg",
            },
            {
                "name": "Academic Senate Meeting",
                "date": "2025-12-02",
                "start_time": "2:30 PM",
                "end_time": "4:00 PM",
                "location": "Community Conference Center - CCC",
                "building_code": "VR",
                "campus": "Virtual",
                "description": """
        <p>The Academic Senate is the representative body of faculty that advises and collaborates with college leadership on academic and professional matters. It ensures faculty have a voice in shaping policies, curriculum, and initiatives that support student success and the college mission.</p>
        <p>Meeting Agendas & Minutes on BoardDocs</p>
        <p><a href='https://go.boarddocs.com/ca/ccccd/Board.nsf/goto?open=&id=D7VQ9H68386F'>https://go.boarddocs.com/ca/ccccd/Board.nsf/goto?open=&id=D7VQ9H68386F</a></p>
        """,
                "event_type": "",
                "image_filename": "5.jpg",
            },
            {
                "name": "Pre-Apprenticeship Information Session",
                "date": "2025-12-02",
                "start_time": "4:00 PM",
                "end_time": "5:30 PM",
                "location": "Virtual",
                "building_code": "VR",
                "campus": "Virtual",
                "description": """
        <p><strong><em>Go beyond the textbook and learn by doing!</em></strong></p>
        <p>The DVC Pre-Apprenticeship Program gives you hands-on experience with modern equipment like CNC machinery and BIM software, preparing you for real job sites from day one. With our strong network of union and employer partners, we don't just teach skills - we open doors to internships, apprenticeships, and lasting careers.</p>
        <p>Join our information session and learn how you can build your future with us! Classes start in Spring 2026.</p>
        """,
                "event_type": "",
                "image_filename": "6.jpg",
            },
            {
                "name": "Step Up Your Pregame: Nutrition Presentation About Pregame Meals",
                "date": "2025-12-02",
                "start_time": "4:00 PM",
                "end_time": "4:45 PM",
                "location": "Virtual",
                "building_code": "VR",
                "campus": "Virtual",
                "description": """
        <p><strong><em>What you eat before a game can be your biggest advantage!</em></strong></p>
        <p>Join the Nutrition Department to unlock the science of pregame meals. Learn how to harness carbs, protein, and fats for maximum energy, perfect your hydration, and create a game-day eating plan that helps you perform at your peak. Open to all DVC athletes, students, and members.</p>
        """,
                "event_type": "",
                "image_filename": "7.jpg",
            },
            {
                "name": "DVC Jazz Combos Concert",
                "date": "2025-12-02",
                "start_time": "7:00 PM",
                "end_time": "8:30 PM",
                "location": "Music - M | 101",
                "building_code": "M",
                "campus": "Pleasant Hill",
                "description": """
        <p>Step into a world of spontaneous creativity as small jazz combos reimagine the classics and explore the cutting edge of contemporary jazz. Experience the art of musical conversation at its most dynamic.</p>
        """,
                "event_type": "",
                "image_filename": "8.jpg",
            },

            # Dec 03
            {
                "name": "Art Department Holiday Art Sale",
                "date": "2025-12-03",
                "start_time": "9:00 AM",
                "end_time": "6:00 PM",
                "location": "Art Complex - A | 101",
                "building_code": "A",
                "campus": "Pleasant Hill",
                "description": """
        <p><strong><em>All proceeds benefit the photography, printmaking and ceramic areas.</em></strong></p>
        <p>Discover one-of-a-kind ceramics, prints, and photographs, each piece born in our classrooms and crafted by the hands of DVC's talented artists – our faculty, students, and staff.</p>
        <p>This is more than a sale; it's a chance to own a piece of our creative journey and directly support the next generation of artists.</p>
        """,
                "event_type": "",
                "image_filename": "9.jpg",
            },
            {
                "name": "DVC Holiday Market - Fundraiser for Student Services Emergency Fund",
                "date": "2025-12-03",
                "start_time": "10:00 AM",
                "end_time": "2:00 PM",
                "location": "Commons Plaza",
                "building_code": "CP",
                "campus": "Pleasant Hill",
                "description": """
        <p>Embrace the holiday spirit with unique shopping, festive cheer, and a special raffle.</p>
        <p>Your visit and participation directly support fellow students through the Student Services Emergency Fund and veterans services.</p>
        """,
                "event_type": "",
                "image_filename": "10.jpg",
            },
            {
                "name": "CalFresh Day",
                "date": "2025-12-03",
                "start_time": "12:00 PM",
                "end_time": "2:00 PM",
                "location": "West Building - W | Learning Commons",
                "building_code": "SR-WEST",
                "campus": "San Ramon",
                "description": """
        <p>Buying groceries? In this economy? Join us in the San Ramon Campus Learning Commons on the first Wednesday of every month to grab a quick bite and learn about CalFresh eligibility requirements, get help with your EBT application, and more.</p>
        """,
                "event_type": "",
                "image_filename": "11.jpg",
            },
            {
                "name": "Board Game Hours at San Ramon Campus",
                "date": "2025-12-03",
                "start_time": "1:00 PM",
                "end_time": "2:00 PM",
                "location": "Library & Academic Success Center - L & ASC",
                "building_code": "SR-LIB",
                "campus": "San Ramon",
                "description": """
        <p>Join a DVC Counselor and other students for a fun time of playing board games – all DVC students are welcome to enjoy a 1-hour mid-week break from the mental stressors of school.</p>
        <p>Laugh, learn something new, and meet new people. Are you up for the challenge?</p>
        """,
                "event_type": "",
                "image_filename": "12.jpg",
            },
            {
                "name": "College Council Meeting",
                "date": "2025-12-03",
                "start_time": "2:30 PM",
                "end_time": "4:30 PM",
                "location": "Community Conference Center - CCC",
                "building_code": "CCC",
                "campus": "Pleasant Hill",
                "description": """
        <p><strong><em>The College Council meets the 1st, 3rd and 5th Wednesday during the semester</em></strong></p>
        <p>The college has established the College Council as its college-wide governance body to support, facilitate and monitor the overall progress of the college toward achieving its goals as established in the DVC Educational Master Plan.</p>
        <p>Meeting Agendas & Minutes on BoardDocs:</p>
        <p><a href='https://go.boarddocs.com/ca/ccccd/Board.nsf/goto?open=&id=BJQNXA5E460F'>https://go.boarddocs.com/ca/ccccd/Board.nsf/goto?open=&id=BJQNXA5E460F</a></p>
        """,
                "event_type": "",
                "image_filename": "13.jpg",
            },
            {
                "name": "College Council Meeting",
                "date": "2025-12-03",
                "start_time": "2:30 PM",
                "end_time": "4:30 PM",
                "location": "Library & Academic Success Center - L & ASC",
                "building_code": "SR-LIB",
                "campus": "San Ramon",
                "description": """
        <p><strong><em>The College Council meets the 1st, 3rd and 5th Wednesday during the semester</em></strong></p>
        <p>The college has established the College Council as its college-wide governance body to support, facilitate and monitor the overall progress of the college toward achieving its goals as established in the DVC Educational Master Plan.</p>
        <p>Meeting Agendas & Minutes on BoardDocs:</p>
        <p><a href='https://go.boarddocs.com/ca/ccccd/Board.nsf/goto?open=&id=BJQNXA5E460F'>https://go.boarddocs.com/ca/ccccd/Board.nsf/goto?open=&id=BJQNXA5E460F</a></p>
        """,
                "event_type": "",
                "image_filename": "14.jpg",
            },

            # Dec 04
            {
                "name": "CalFresh Day & Pizza on the Patio",
                "date": "2025-12-04",
                "start_time": "12:00 PM",
                "end_time": "2:00 PM",
                "location": "Student Union - SU | 101",
                "building_code": "SU",
                "campus": "Pleasant Hill",
                "description": """
        <p>Buying groceries? In this economy? Join us in the Pleasant Hill Campus Student Union on Thursday to grab a quick bite and learn about CalFresh eligibility requirements, get help with your EBT application, and more.</p>
        """,
                "event_type": "",
                "image_filename": "15.jpg",
            },

            # Dec 05
            {
                "name": "Math Study Jam",
                "date": "2025-12-05",
                "start_time": "2:00 PM",
                "end_time": "6:00 PM",
                "location": "Learning Center - LC | 200",
                "building_code": "LC",
                "campus": "Pleasant Hill",
                "description": """
        <p>Math tutors and faculty will be available to help with any math course.</p>
        <p>Bring your study guides, review packets, and practice exams. Snacks and pizza available while supplies last.</p>
        """,
                "event_type": "",
                "image_filename": "16.jpg",
            },
            {
                "name": "Dance Repertory Production: \"MESSAGES\"",
                "date": "2025-12-05",
                "start_time": "8:00 PM",
                "end_time": "10:00 PM",
                "location": "Performing Arts Center - PAC",
                "building_code": "PAC",
                "campus": "Pleasant Hill",
                "description": """
        <p>Experience the full spectrum of movement in a single production.</p>
        <p>This curated performance features original works by faculty and guest choreographers, showcasing a breathtaking range of styles—from the grace of Ballet and Modern to the energy of Hip-Hop, Jazz, K-Pop, and Latin dance.</p>
        <p><strong>Ticket Price: $20 General Admission, $16 Staff/Faculty/Seniors, $12 Students, $12 Kids (12 years-old and under)</strong></p>
        """,
                "event_type": "",
                "image_filename": "17.jpg",
            },

            # Dec 06
            {
                "name": "Dance Repertory Production: \"MESSAGES\"",
                "date": "2025-12-06",
                "start_time": "8:00 PM",
                "end_time": "10:00 PM",
                "location": "Performing Arts Center - PAC",
                "building_code": "PAC",
                "campus": "Pleasant Hill",
                "description": """
        <p>Experience the full spectrum of movement in a single production.</p>
        <p>This curated performance features original works by faculty and guest choreographers, showcasing a breathtaking range of styles—from the grace of Ballet and Modern to the energy of Hip-Hop, Jazz, K-Pop, and Latin dance.</p>
        <p><strong>Ticket Price: $20 General Admission, $16 Staff/Faculty/Seniors, $12 Students, $12 Kids (12 years-old and under)</strong></p>
        """,
                "event_type": "",
                "image_filename": "18.jpg",
            },

            # Dec 07
            {
                "name": "Dance Repertory Production: \"MESSAGES\"",
                "date": "2025-12-07",
                "start_time": "2:00 PM",
                "end_time": "4:00 PM",
                "location": "Performing Arts Center - PAC",
                "building_code": "PAC",
                "campus": "Pleasant Hill",
                "description": """
        <p>Experience the full spectrum of movement in a single production.</p>
        <p>This curated performance features original works by faculty and guest choreographers, showcasing a breathtaking range of styles—from the grace of Ballet and Modern to the energy of Hip-Hop, Jazz, K-Pop, and Latin dance.</p>
        <p><strong>Ticket Price: $20 General Admission, $16 Staff/Faculty/Seniors, $12 Students, $12 Kids (12 years-old and under)</strong></p>
        """,
                "event_type": "",
                "image_filename": "19.jpg",
            },
            {
                "name": "Budget Committee Meeting",
                "date": "2025-12-07",
                "start_time": "3:00 PM",
                "end_time": "5:00 PM",
                "location": "Administration Building - AB | 108",
                "building_code": "AB",
                "campus": "Pleasant Hill",
                "description": """
        <p>The college established a Budget Committee to ensure a representative body of the college community is educated regarding all aspects of the college budget and actively participates in recommending resource allocations.</p>
        <p>This body is responsible to ensure resource allocation follows established budget process, which aligns resource allocation with institutional planning and ensures transparency, financial stability and integrity.</p>
        <p>Meeting Agendas & Minutes on BoardDocs:</p>
        <p><a href='https://go.boarddocs.com/ca/ccccd/Board.nsf/goto?open=&id=BJQNX55E3FE5'>https://go.boarddocs.com/ca/ccccd/Board.nsf/goto?open=&id=BJQNX55E3FE5</a></p>
        """,
                "event_type": "",
                "image_filename": "20.jpg",
            },
            {
                "name": "DVC Guitar Ensemble Concert",
                "date": "2025-12-07",
                "start_time": "7:00 PM",
                "end_time": "8:30 PM",
                "location": "Performing Arts Center - PAC",
                "building_code": "PAC",
                "campus": "Pleasant Hill",
                "description": """
        <p>Our talented intermediate and advanced guitarists explore the full range of their instrument.</p>
        <p>Experience a diverse repertoire of classical, jazz, and world music, brilliantly adapted for an unforgettable ensemble performance.</p>
        """,
                "event_type": "",
                "image_filename": "21.jpg",
            },

            # Dec 08
            {
                "name": "Finals Week Coffee and Snacks",
                "date": "2025-12-08",
                "start_time": "9:00 AM",
                "end_time": "6:00 PM",
                "location": "Learning Center - LC | 200",
                "building_code": "LC",
                "campus": "Pleasant Hill",
                "description": """
        <p>Power through your finals with complimentary coffee and snacks, available all week in the Math & Engineering Student Center.</p>
        <p>We've got your fuel - you focus on your focus.</p>
        """,
                "event_type": "",
                "image_filename": "22.jpg",
            },
            {
                "name": "Student Equity & Success Committee",
                "date": "2025-12-08",
                "start_time": "2:30 PM",
                "end_time": "4:30 PM",
                "location": "Student Services Center - SSC | 232",
                "building_code": "SSC",
                "campus": "Pleasant Hill",
                "description": """
        <p>The Student Equity and Success Committee monitors, evaluates and advances the institutional level progress on achieving the Educational Master Plan outcomes for equitable student success.</p>
        <p>The committee supports the college’s efforts to improve equitable student success. It also makes recommendations on how to improve the student experience, college-wide and community outcomes, providing a holistic framework to understand and improve the conditions impacting student success.</p>
        <p>Meeting Agendas & Minutes on BoardDocs:</p>
        <p><a href='https://go.boarddocs.com/ca/ccccd/Board.nsf/goto?open=&id=D7VQ7D67E890'>https://go.boarddocs.com/ca/ccccd/Board.nsf/goto?open=&id=D7VQ7D67E890</a></p>
        <p>Student Equity and Success Committee meets every 2nd Monday during the semester.</p>
        """,
                "event_type": "",
                "image_filename": "23.jpg",
            },
            {
                "name": "Curriculum Committee Meeting",
                "date": "2025-12-08",
                "start_time": "2:30 PM",
                "end_time": "4:00 PM",
                "location": "Community Conference Center - CCC",
                "building_code": "VR",
                "campus": "Virtual",
                "description": """
        <p>The Curriculum Committee oversees the college curriculum and makes recommendations to the Vice President of Instruction regarding new courses and programs, degree, certificate and transfer requirements including General Education requirements, and other matters which concern curriculum.</p>
        <p>Meeting Agendas & Minutes on BoardDocs:</p>
        <p><a href='https://go.boarddocs.com/ca/ccccd/Board.nsf/goto?open=&id=D7VQF968FEF0'>https://go.boarddocs.com/ca/ccccd/Board.nsf/goto?open=&id=D7VQF968FEF0</a></p>
        """,
                "event_type": "",
                "image_filename": "24.jpg",
            },

            # Dec 09
            {
                "name": "Finals Week Coffee and Snacks",
                "date": "2025-12-09",
                "start_time": "9:00 AM",
                "end_time": "6:00 PM",
                "location": "Learning Center - LC | 200",
                "building_code": "LC",
                "campus": "Pleasant Hill",
                "description": """
        <p>Power through your finals with complimentary coffee and snacks, available all week in the Math & Engineering Student Center.</p>
        <p>We've got your fuel - you focus on your focus.</p>
        """,
                "event_type": "",
                "image_filename": "25.jpg",
            },
            {
                "name": "DVC Songwriters' Showcase",
                "date": "2025-12-09",
                "start_time": "7:00 PM",
                "end_time": "8:30 PM",
                "location": "Music - M | 101",
                "building_code": "M",
                "campus": "Pleasant Hill",
                "description": """
        <p>Witness the future of music as Songwriting students (MUSX-182/282) debut their original works, brought to life by the expert live sound production of AV Essentials (MUSX-100/150LS) students.</p>
        <p>It’s a raw, authentic, and unforgettable showcase of DVC talent from composition to concert.</p>
        """,
                "event_type": "",
                "image_filename": "26.jpg",
            },

            # Dec 10
            {
                "name": "Finals Week Coffee and Snacks",
                "date": "2025-12-10",
                "start_time": "9:00 AM",
                "end_time": "6:00 PM",
                "location": "Learning Center - LC | 200",
                "building_code": "LC",
                "campus": "Pleasant Hill",
                "description": """
        <p>Power through your finals with complimentary coffee and snacks, available all week in the Math & Engineering Student Center.</p>
        <p>We've got your fuel - you focus on your focus.</p>
        """,
                "event_type": "",
                "image_filename": "27.jpg",
            },
            {
                "name": "Research, Planning, and Evaluation Committee (RPEC)",
                "date": "2025-12-10",
                "start_time": "2:30 PM",
                "end_time": "4:30 PM",
                "location": "Administration Building - AB | President's Office Conference Room",
                "building_code": "AB",
                "campus": "Pleasant Hill",
                "description": """
        <p>The Research, Planning, and Evaluation Committee (RPEC), taking direction from College Council, supports the work of the college to achieve its Educational Master Plan, annual priorities, and other objectives.</p>
        <p>RPEC promotes data-informed decision-making throughout the college, supporting a culture of evaluation and alignment of all existing college plans.</p>
        <p>RPEC meets the second Wednesday of the month during the semester.</p>
        <p>Meeting Agendas & Minutes on BoardDocs:</p>
        <p><a href='https://go.boarddocs.com/ca/ccccd/Board.nsf/goto?open=&id=BJQP2F5E56A0'>https://go.boarddocs.com/ca/ccccd/Board.nsf/goto?open=&id=BJQP2F5E56A0</a></p>
        """,
                "event_type": "",
                "image_filename": "28.jpg",
            },

            # Dec 11
            {
                "name": "Finals Week Coffee and Snacks",
                "date": "2025-12-11",
                "start_time": "9:00 AM",
                "end_time": "6:00 PM",
                "location": "Learning Center - LC | 200",
                "building_code": "LC",
                "campus": "Pleasant Hill",
                "description": """
        <p>Power through your finals with complimentary coffee and snacks, available all week in the Math & Engineering Student Center.</p>
        <p>We've got your fuel - you focus on your focus.</p>
        """,
                "event_type": "",
                "image_filename": "29.jpg",
            },
            {
                "name": "Information and Instructional Technology Committee (IITC) Meeting",
                "date": "2025-12-11",
                "start_time": "2:00 PM",
                "end_time": "4:00 PM",
                "location": "Virtual",
                "building_code": "VR",
                "campus": "Virtual",
                "description": """
        <p>The Information and Instructional Technology Committee (IITC) researches, prioritizes and recommends technology-centered outcomes that directly or indirectly impact equitable student success and the core values of DVC.</p>
        <p>Meeting Agendas & Minutes on SharePoint (InSite credentials required):</p>
        <p><a href='https://email4cd.sharepoint.com/:f:/r/sites/IITC/Shared%20Documents/General/IITC%20Agenda%20%26%20Meeting?csf=1&web=1&e=XSFqzP'>IITC Agenda & Meeting</a></p>
        """,
                "event_type": "",
                "image_filename": "30.jpg",
            },
        ]

        for ev in event_data:
            event = Events.objects.create(
                author_ID=author,
                name=ev["name"],
                description=ev["description"],
                date=ev["date"],
                start_time=ev["start_time"],
                end_time=ev["end_time"],
                location=ev["location"],
                building_code=ev["building_code"],
                campus=ev["campus"],
                event_type=ev.get("event_type") or "General",
            )

            # Attach existing image from folder
            event.image.name = os.path.join("events", ev["image_filename"])
            event.save()  # save after setting image
            events_created += 1

        print(f"Created {events_created} sample events.")

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        # Connect the function to run after migrations
        post_migrate.connect(populate_default_data, sender=self)