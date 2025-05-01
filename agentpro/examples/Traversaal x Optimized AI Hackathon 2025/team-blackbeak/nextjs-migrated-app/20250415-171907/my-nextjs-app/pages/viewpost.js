import React from 'react';
import Header from '../components/Header';
import Navigation from '../components/Navigation';
import Footer from '../components/Footer';

const ViewPost = ({ posts, username }) => (
  <>
    <Header />
    <Navigation username={username} />
    <div className="content">
      <table>
        <thead>
          <tr>
            <th>Id</th>
            <th>Title</th>
            <th>Author</th>
            <th>Keyword</th>
            <th>Image</th>
            <th>Content</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          {posts.map((post) => (
            <tr key={post.id}>
              <td>{post.id}</td>
              <td>{post.title}</td>
              <td>{post.author}</td>
              <td>{post.keyword}</td>
              <td><img src={`/image/${post.image}`} height="100" width="100" alt={post.title} /></td>
              <td>{post.content}</td>
              <td>{post.date}</td>
              <td><a href={`/updateposts?id=${post.id}`}>Update</a></td>
              <td><a href={`/deletepost?id=${post.id}`}>Delete</a></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    <Footer />
  </>
);

export async function getServerSideProps({ req }) {
  const { username } = req.session;

  if (!username) {
    return {
      redirect: {
        destination: '/',
        permanent: false,
      },
    };
  }

  const res = await fetch('http://localhost:3000/api/viewpost');
  const posts = await res.json();

  return { props: { posts, username } };
}

export default ViewPost;