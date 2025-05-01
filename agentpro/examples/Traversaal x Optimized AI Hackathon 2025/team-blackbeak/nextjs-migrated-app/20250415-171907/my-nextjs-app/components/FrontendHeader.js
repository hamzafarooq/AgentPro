import React from 'react';
import Link from 'next/link';

const FrontendHeader = () => (
  <div className="header">
    <div className="menu">
      <li><Link href="/">HOME</Link></li>
      <li><Link href="/blogs">BLOGS</Link></li>
      <li><Link href="/aboutus">ABOUT US</Link></li>
      <li><Link href="/contactus">CONTACT US</Link></li>
    </div>
  </div>
);

export default FrontendHeader;