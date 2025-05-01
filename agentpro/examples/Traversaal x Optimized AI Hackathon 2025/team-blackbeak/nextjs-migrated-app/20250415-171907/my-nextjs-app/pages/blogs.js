import React from 'react';
import FrontendHeader from '../components/FrontendHeader';
import FrontendContent from '../components/FrontendContent';
import FrontendNavigation from '../components/FrontendNavigation';
import FrontendFooter from '../components/FrontendFooter';

const Blogs = ({ posts, pageNo, totalPages, recentPosts }) => (
  <>
    <FrontendHeader />
    <FrontendContent posts={posts} pageNo={pageNo} totalPages={totalPages} />
    <FrontendNavigation posts={recentPosts} />
    <FrontendFooter />
  </>
);

export async function getServerSideProps({ query }) {
  const pageNo = query.page_no || 1;
  const res = await fetch(`http://localhost:3000/api/viewpost?page_no=${pageNo}`);
  const posts = await res.json();

  const totalRes = await fetch('http://localhost:3000/api/viewpost');
  const totalPosts = await totalRes.json();
  const totalPages = Math.ceil(totalPosts.length / 2);

  const recentRes = await fetch('http://localhost:3000/api/viewpost?limit=2');
  const recentPosts = await recentRes.json();

  return { props: { posts, pageNo, totalPages, recentPosts } };
}

export default Blogs;