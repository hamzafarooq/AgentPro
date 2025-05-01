import React from 'react';
import FrontendHeader from '../components/FrontendHeader';
import FrontendContent from '../components/FrontendContent';
import FrontendNavigation from '../components/FrontendNavigation';
import FrontendFooter from '../components/FrontendFooter';

const Home = ({ posts, recentPosts }) => (
  <>
    <FrontendHeader />
    <FrontendContent posts={posts} pageNo={1} totalPages={Math.ceil(posts.length / 2)} />
    <FrontendNavigation posts={recentPosts} />
    <FrontendFooter />
  </>
);

export async function getServerSideProps() {
  const res = await fetch('http://localhost:3000/api/viewpost');
  const posts = await res.json();

  const recentRes = await fetch('http://localhost:3000/api/viewpost?limit=2');
  const recentPosts = await recentRes.json();

  return { props: { posts, recentPosts } };
}

export default Home;