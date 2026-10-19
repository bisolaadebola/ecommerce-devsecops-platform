// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

import Link from 'next/link';
import * as S from './Banner.styled';

const Banner = () => {
  return (
    <S.Banner>
      <S.ImageContainer>
        <S.BannerImg />
      </S.ImageContainer>
      <S.TextContainer>
        <S.Title>Welcome to DigitalWitch</S.Title>
        <S.Subtitle>Professional Cloud Security + DevOps Training</S.Subtitle>
        <Link href="#hot-products"><S.GoShoppingButton>Explore the Store</S.GoShoppingButton></Link>
      </S.TextContainer>
    </S.Banner>
  );
};

export default Banner;
