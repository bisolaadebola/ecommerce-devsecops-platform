// Copyright The OpenTelemetry Authors
// SPDX-License-Identifier: Apache-2.0

import { DefaultTheme } from 'styled-components';

const Theme: DefaultTheme = {
  colors: {
    // DigitalWitch brand (key names kept from the upstream demo)
    otelBlue: '#1F6FD1', // brand blue: buttons, links

    otelYellow: '#C8902E', // brand gold: accents
    otelGray: '#0B1F3A', // deep navy
    otelRed: '#FB7181',
    backgroundGray: 'rgba(31, 111, 209, 0.08)',
    lightBorderGray: 'rgba(31, 111, 209, 0.3)',
    borderGray: '#0B1F3A',
    textGray: '#0B1F3A',
    textLightGray: '#78788C',
    white: '#FFFFFF',
  },
  breakpoints: {
    desktop: '@media (min-width: 768px)',
  },
  sizes: {
    mxLarge: '22px',
    mLarge: '20px',
    mMedium: '14px',
    mSmall: '12px',
    dxLarge: '58px',
    dLarge: '40px',
    dMedium: '18px',
    dSmall: '16px',
    nano: '8px',
  },
  fonts: {
    bold: '800',
    regular: '500',
    semiBold: '700',
    light: '400',
  },
};

export default Theme;
