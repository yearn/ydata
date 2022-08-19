/* eslint-disable react/react-in-jsx-scope */
/* eslint-disable @typescript-eslint/explicit-function-return-type */

const GITHUB_URI = 'https://github.com/huggingbot/messari-frontier-web'

export default {
  docsRepositoryBase: GITHUB_URI,
  feedbackLabels: 'feedback',
  feedbackLink: 'Question? Give us feedback →',
  floatTOC: true,
  footerEditLink: 'Edit this page on GitHub',
  footerText: () => (
    <div className={'text-sm text-current'}>
      {'Yearn Finance '}
      {new Date().getFullYear()}
    </div>
  ),
  GITHUB_URI,
  head: ({ meta, title }) => {
    return (
      <>
        <title>{meta.name}</title>
        <meta httpEquiv={'X-UA-Compatible'} content={'IE=edge'} />
        <meta
          name={'viewport'}
          content={'minimum-scale=1, initial-scale=1, width=device-width, shrink-to-fit=no, viewport-fit=cover'}
        />
        <meta name={'description'} content={meta.name} />
        <meta name={'msapplication-TileColor'} content={meta.title_color} />

        <meta name={'application-name'} content={meta.name} />
        <meta name={'apple-mobile-web-app-title'} content={meta.name} />
        <meta name={'apple-mobile-web-app-capable'} content={'yes'} />
        <meta name={'apple-mobile-web-app-status-bar-style'} content={'default'} />
        <meta name={'format-detection'} content={'telephone=no'} />
        <meta name={'mobile-web-app-capable'} content={'yes'} />
        <meta name={'msapplication-config'} content={'/favicons/browserconfig.xml'} />
        <meta name={'msapplication-tap-highlight'} content={'no'} />

        <link rel={'manifest'} href={'/manifest.json'} />
        <link rel={'mask-icon'} href={'/favicons/safari-pinned-tab.svg'} color={meta.theme_color} />

        <link rel={'shortcut icon'} type={'image/x-icon'} href={'/favicons/favicon.ico'} />
        <link rel={'icon'} type={'image/png'} sizes={'32x32'} href={'/favicons/favicon-32x32.png'} />
        <link rel={'icon'} type={'image/png'} sizes={'16x16'} href={'/favicons/favicon-16x16.png'} />
        <link rel={'icon'} type={'image/png'} sizes={'512x512'} href={'/favicons/favicon-512x512.png'} />
        <link rel={'icon'} type={'image/png'} sizes={'192x192'} href={'/favicons/android-icon-192x192.png'} />
        <link rel={'icon'} type={'image/png'} sizes={'144x144'} href={'/favicons/android-icon-144x144.png'} />
        <link rel={'apple-touch-icon'} href={'/favicons/apple-icon.png'} />
        <link rel={'apple-touch-icon'} sizes={'152x152'} href={'/favicons/apple-icon-152x152.png'} />
        <link rel={'apple-touch-icon'} sizes={'180x180'} href={'/favicons/apple-icon-180x180.png'} />
        <link rel={'apple-touch-icon'} sizes={'167x167'} href={'/favicons/apple-icon-167x167.png'} />

        <meta name={'robots'} content={'index,nofollow'} />
        <meta name={'googlebot'} content={'index,nofollow'} />
        <meta charSet={'utf-8'} />

        <script
          lang={'javascript'}
          dangerouslySetInnerHTML={{
            __html: `if (!window.localStorage.getItem("theme_default")) {
						window.localStorage.setItem("theme", "dark");
						window.localStorage.setItem("theme_default", "dark");
						document.documentElement.classList.add("dark");
						document.documentElement.classList.remove("light");
						}`,
          }}
        />
      </>
    )
  },
  logo: () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    return (
      <>
        <div className={'mr-4'}>
          <svg width={'40'} height={'40'} viewBox={'0 0 1024 1024'} fill={'none'} xmlns={'http://www.w3.org/2000/svg'}>
            <circle cx={'512'} cy={'512'} r={'512'} fill={'#FF90A1'} />
            <path
              d={
                'M645.095 167.388L512.731 345.535L501.031 330.202L378.173 168.118L295.537 229.447L460.078 449.941V609.105H564.653V449.21L728.463 229.447L645.095 167.388Z'
              }
              fill={'white'}
            />
            <path
              d={
                'M688.242 392.992L623.888 474.764C654.602 503.969 673.616 545.585 673.616 590.852C673.616 679.925 601.218 752.206 512 752.206C422.782 752.206 350.384 679.925 350.384 590.852C350.384 544.855 370.129 503.239 400.844 474.034L337.221 391.532C280.912 439.719 245.81 511.27 245.81 590.852C245.81 737.604 365.01 856.612 512 856.612C658.99 856.612 778.191 737.604 778.191 590.852C778.191 512 743.089 441.179 688.242 392.992Z'
              }
              fill={'white'}
            />
          </svg>
        </div>
        <span className={'hidden text-xl font-bold md:inline text-neutral-0 font-roboto'}>
          {'Messari Frontier Web'}
        </span>
      </>
    )
  },
  nextLinks: true,
  nextThemes: { defaultTheme: 'dark' },
  darkMode: true,
  prevLinks: true,
  projectLink: GITHUB_URI,
  search: true,
  titleSuffix: ' – Yearn',
  unstable_flexsearch: true,
}
