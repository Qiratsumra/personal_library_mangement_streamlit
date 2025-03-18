import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie # type: ignore
import requests

# set page configuration
st.set_page_config(page_icon='📘', page_title='Library Mangement', layout='wide', initial_sidebar_state='expanded')

# Defined Custom CSS
st.markdown('''
<style>
       .main-header { 
                      font-size:3rem !important; 
                      color: #1E3A8A; 
                      font-weight: 600; 
                      margin-bottom: 1rem; 
                      text-align: center; 
                      text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }

       .sub_header { 
                     font-size: 1.8rem !important; 
                     color: #3B82F6; 
                     font-weight:500; 
                     margin-top: 1rem; 
                     margin-bottom: 1rem; 
       }

       .success_message { 
                          padding: 1rem; 
                          background-color: #ECFDF5; 
                          border-left: 5px solid #10B981; 
                          border-radius: 0.375rem;
       }

       .warning_message { 
                          padding: 1rem; 
                          background-color: #FEF3C7; 
                          border-left :5px solid #F59E0B; 
                          border-radius: 0.375rem
       }

       .book-card { 
                    background-color: #F3F4F6;
                    border-radius: 0.5rem;
                    padding: 1rem; 
                    margin-bottom : 1rem;
                    border-left: 5px solid #3B82F6;
                    treansition: transform 0.3s ease;
       }

       ..book-card-hover{ 
                          transform : translateY(-5px)
                          box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1)
       }

       .read-badge {
                     background-color: #10B981;
                     color: white;
                     padding: 0.25rem 0.75rem;
                     border-radius: 1rem;
                     font-size: 0.875rem;
                     font-weight: 600  
        }
       .action-button { 
                        margin-right: 0.5rem
        }
       .stButton>button{ 
                         border-radius: 0.375rem;
        }

</style>
''',unsafe_allow_html=True)

def load_lottieurl(url):
   try:
       response = requests.get(url)
       if response.status_code !=200:
           return None
       return response.json()
   except:
       return None

if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_result' not in st.session_state:
    st.session_state.search_result = []
if 'addBooks' not in st.session_state:
    st.session_state.addBooks = []
if 'removeBooks' not in st.session_state:
    st.session_state.removeBooks = []
if 'currentView' not in st.session_state:
    st.session_state.currentView = "library"

# Load Library
def loadLibrary():
    try :
        if os.path.exists('library.json'):
            with open('library.json','r') as file:
                st.session_state.library =json.load(file)
                return True
            return False
    except Exception as e :
        st.error(f'Error Loading Library: {e}')
        return False
    
# Save Library
def saveLibrary():
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file)
            return True
    except Exception as e:
        st.error(f'Error Saving Library: {e}')
        return False

# Now Add Books to library
def addBooks(author,book_title, publish_year,genre, read_status):
    book = {
        'author': author,
        'title': book_title,
        'publish_year': publish_year,
        'genre': genre,
        'read_book_status': read_status,
        'add_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    st.session_state.library.append(book)
    saveLibrary()
    st.session_state.addBooks.append = True
    time.sleep(1)
    
# Now for Remove a book
def removeBooks(index):
    if 0 <= index < len(st.session_state.library): 
        # used del key word to delete the book
        del st.session_state.library[index]
        saveLibrary()
        st.session_state.removeBooks =True
        return True
    return False

# Now Serach Book in library
def searchBooks(searchTream, searchBy):
    searchTream = searchTream.lower()
    result = []
    for book in st.session_state.library:
        if searchBy == 'Title' and searchTream in book['title'].lower():
            result.append(book)
        elif searchBy == 'Author' and searchTream in book['author'].lower():
            result.append(book)
        elif searchBy == 'Genre' and searchTream in book['genre'].lower():
            result.append(book)
    st.session_state.search_result = result

# Calculatr library status
def library_get_status():
    totalBooks = len(st.session_state.library)
    readBooks = sum(1 for book in st.session_state.library if book['read status'])
    read_book_percent = (readBooks/totalBooks*100) if totalBooks > 0  else 0
    geners = {}
    authors = {}
    decades = {}

    for book in st.session_state.library:
        if book['genre'] in geners:
            geners[book['genre']] +=1
        else :
            geners[book['genre']] = 1

        # count author
        if book['author'] in authors:
            authors[book['author']] +=1
        else :
            authors[book['author']] = 1

        # now for decades
        decades = (book['publish_year'] //10)*10
        if decades in decades:
            decades[decades] +=1
        else:
            decades[decades] =1
    
    # sort by count
    geners = dict(sorted(geners.items(), key=lambda x:[1], reverse=True))
    authors = dict(sorted(authors.items(), key=lambda x:[1],reverse=True))
    decades = dict(sorted(decades.items(),key=lambda x:[1], reverse=True))

    return {
     'total_books':totalBooks,
     'read_book':readBooks,
     'read_book_status':   read_book_percent,
     'genre': geners,
     'author': authors,
     'decades': decades
    }


def create_visulation(stats):
    if stats['total_books'] > 0 :
        fig_read_status = go.Figure(data=[go.Pie(
            labels = ['Read','Unread'],
            values = [stats['read_books'], stats['total_Books'] - stats['read_book']],
            hole = 0.4,
            marker_color = ['#10B981','#F87171']
        )])
        fig_read_status.update_layout(
            title_text = 'Read VS Unread Books',
            showlegend =True,
            height = 400
        )
        st.plotly_chart(fig_read_status, use_container_width=True)
    
    # Bar chart for genre
    if stats['genre']:
        genre_df = pd.DataFrame({
            'Genre': list(stats['genre'].keys()),
            'Count':list(stats['genre'].values())
        })
        fig_genres = px.bar(
            genre_df,
            x='Genre',
            y='Count',
            color = 'Count',
            color_continous_scale = px.color.sequental.Blues
        )
        fig_genres.update_layout(
            title_text = 'Book by publication decades',
            xaxis_title = 'Decade',
            yaxis_title = 'Number of books',
            height = 400
        )
        st.plotly_chart(fig_genres, use_container_width=True)
    
    if stats['decades']:
        decades_df  = pd.DataFrame({
            'Decade': [f'{decade}s'for decade in stats['decades'].keys()],
            'Count':list(stats['decades'].values())
        })
        fig_decades = px.line(
            decades_df,
            x= 'Decade',
            y='Count',
            markers = True,
            line_sape = 'spline'
        )
        fig_decades.update_layout(
            title_text = 'Book by publication decade',
            xaxis_title = 'Decade',
            yaxis_title = 'Number of book',
            height =400
        )
        st.plotly_chart(fig_decades,use_container_width=True)

# Load Library
loadLibrary()
st.sidebar.markdown('<h1 style = "text-align:center;">Naviagtion</h1>', unsafe_allow_html=True)
lottie_book=load_lottieurl('https://assets9.lottieflies.com/temp/1f20_aKAfIn.json')
if lottie_book:
    with st.sidebar:
        st_lottie(lottie_book,height=200, key='book_animation')
nav_option = st.sidebar.radio(
    'Choose an option',
    ['View Library', 'Add Book', 'Search Books','Library Statistics'])
if nav_option == 'View Library':
    st.session_state.currentView = 'library'
elif nav_option == 'Add Book':
    st.session_state.currentView = 'addBooks'
elif nav_option == 'Search Book':
    st.session_state.currentView = 'search'
elif nav_option == 'Library Statistics':
    st.session_state.currentView = 'stats'

st.markdown('<h1 class="main-header">Personal Library Mangement Sytem</h1>', unsafe_allow_html=True)
if st.session_state.currentView == 'addBooks':
    st.markdown('<h2 class="sub_header">Add a new book </h2>', unsafe_allow_html=True)
    # Add Books Input for Adding a Book
    with st.form(key='add_book_form'):
        col1,col2 = st.columns(2)
        # for col1
        with col1:
            title = st.text_input('Book Title',max_chars=100) 
            author = st.text_input('Author', max_chars=100)
            publish_year = st.number_input('Publication Year', min_value=1000 , max_value=datetime.now().year, step=1, value=2023)
        
        # for col2
        with col2:
            genre = st.selectbox('Genre',['Friction', 'Education', 'Science', 'Technology','Novels'])
            read_status = st.radio('Read Status',['Read', 'Unread'], horizontal=True)
            read_bool = read_status  == 'Read'
        submit_button = st.form_submit_button(label='Add Book')
        if submit_button and title and author:
            addBooks(title,author, publish_year, genre,read_bool)
    
    if st.session_state.addBooks:
        st.markdown('<div class="success_message">Book Added Successfully!</div>', unsafe_allow_html=True)
        st.balloons()
        st.session_state.addBooks = False
    else:
        st.session_state.currentView =='library'
        st.markdown('<h2 class "sub_header">Your Library</h2>',unsafe_allow_html=True)

        if not st.session_state.library:
            st.markdown('<div class "warning_message">Your Library is empty. Add some books.</div>',unsafe_allow_html=True)
        else:
            cols = st.columns(2)
            for i ,book in enumerate(st.session_state.library):
                with cols[i%2]:
                    st.markdown(f''' <div class = "book-card">
                                <h2>{book['title']}</h2>
                                <p><strong>Author</strong>:{book['author']}</p>
                                <p><strong>Publish Year</strong>:{book['publish_year']}</p>
                                <p><strong>Genre</strong>:{book['genre']}</p>
                                <p><span class="{'read-badge' if book['read_status'] else 'unread-badge'}">{'Read' if book['read_status'] else 'Unread'}</span><p/>
                                </div> ''', unsafe_allow_html=True)
                    col1,col2 = st.columns(2)
                    with col1:
                        if st.button(f'Remove',key=f"remove_{i}",use_container_width=True):
                            if removeBooks(i):
                                st.rerun()
                    with col2:
                        new_status =not book['read_status']
                        status_label = 'Mark as read' if not book['read_status'] else 'Mark as Unread'
                        if st.button(status_label,key=f"status_{i}", use_container_width=True):
                            st.session_state.library[i]['read_status'] = new_status
                            saveLibrary()
                            st.rerun()
    if st.session_state.removeBooks:
        st.markdown('<div class ="success_message">Book Removed Successfully! </div>', unsafe_allow_html=True)
        st.session_state.removeBook = False
    elif st.session_state.currentView == 'search':
        st.markdown('<h2 class="sub_header">Search Books</h2>', unsafe_allow_html=True)
    
    search_by = st.selectbox('Search By:'['Title','Author','Genre'])
    search_tearm = st.text_input('Enter search tearm:')

    if st.button('Search', use_container_width=False):
        if search_tearm:
            with st.spinner('Searching....'):
                time.sleep(1)
                searchBooks(search_tearm,search_by)
    if hasattr(st.session_state, 'search_result'):
        if st.session_state.search_result:
            st.markdown(f'<h3>Found {len(st.session_state.search_result)} result:</h3>', unsafe_allow_html=True)
            st.markdown(f''' <div class = "book-card">
                                <h2>{book['title']}</h2>
                                <p><strong>Author</strong>:{book['author']}</p>
                                <p><strong>Publish Year</strong>:{book['publish_year']}</p>
                                <p><strong>Genre</strong>:{book['genre']}</p>
                                <p><span class="{'read-badge' if book['read_status'] else 'unread-badge'}">{'Read' if book['read_status'] else 'Unread'}</span><p/>
                                </div> ''', unsafe_allow_html=True)
        elif search_tearm:
            st.markdown("<div class='warning message'>No book found matching</div>", unsafe_allow_html=True)

elif st.session_state.currentView == 'stats':
    st.markdown('<h2 class ="sub_header">Library Statics</h2>', unsafe_allow_html=True)

    if not st.session_state.library:
        st.markdown('<div class="warning_message">Your Library is empty. Add books.</div>', unsafe_allow_html=True)
    else:
        stats = library_get_status()
        col1,col2,col3 = st.columns(3)
        with col1:
            st.metric('Total Books',stats['total_books'])
        with col2:
            st.metric('Read Books', stats['read_books'])
        with col3:
            st.metric('Read Books Percentage',f'{stats['percentage_read'] :.1f}%')
        create_visulation()

        if stats['author']:
            st.markdown('<h3>Top Authors</h3>', unsafe_allow_html=True)
            top_authors =  dict(list(stats['author'].items())[:5])
            for author, count in top_authors.items():
                st.markdown(f'**{author}**: {count} book{'s' if count>1 else ''}')
st.markdown('---------------------')
st.markdown('Copyright @2025 Qirat Saeed Personal Library Mangement System', unsafe_allow_html=True)