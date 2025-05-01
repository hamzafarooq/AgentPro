import React from 'react';
import FrontendHeader from '../components/FrontendHeader';
import FrontendFooter from '../components/FrontendFooter';

const ReadMoreAll = ({ post }) => (
  <>
    <FrontendHeader />
    <div className="content">
      <ul style={{ listStyle: 'none', fontFamily: "'Courier New', Courier, monospace", color: '#999999', border: 'solid 5px #000033' }}>
        <li>{post.date}</li>
        <li>{post.title}</li>
        <li>{post.author}</li>
        <li>{post.keyword}</li>
        <li><img src={`/image/${post.image}`} height="100px" width="150px" alt={post.title} /></li>
        <li>{post.content}</li>
      </ul>
    </div>
    <FrontendFooter />
  </>
);

export async function getServerSideProps({ query }) {
  const res = await fetch(`http://localhost:3000/api/viewpost?id=${query.id}`);
  const post = await res.json();

  return { props: { post } };
}

export default ReadMoreAll;