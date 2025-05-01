import React from 'react';
import Link from 'next/link';

const Navigation = ({ username }) => (
  <div className="navigation">
    <ul>
      <li>WELCOME {username}</li>
      <li><Link href="/addpost">Add Posts</Link></li>
      <li><Link href="/viewpost">View Posts</Link></li>
      <li><Link href="/addusers">Add Users</Link></li>
      <li><Link href="/viewusers">View Users</Link></li>
      <li><Link href="/logout">Log Out</Link></li>
    </ul>
  </div>
);

export default Navigation;