/* eslint-disable react/react-in-jsx-scope */
/* eslint-disable @typescript-eslint/explicit-function-return-type */
import LogoYearn from 'components/icons/LogoYearn';

const GITHUB_URI = 'https://github.com/yearn/yearn-data-analytics';

export default {
	docsRepositoryBase: GITHUB_URI,
	feedback: {labels: 'feedback', content: 'Question? Give us feedback →'},
	sidebar: {defaultMenuCollapsed: true},
	editLink: {text:'Edit this page on GitHub'},
	footer: {component: null},
	GITHUB_URI,
	head: (
		<>
			<title>{'Yearn Data Analytics'}</title>
			<meta httpEquiv={'X-UA-Compatible'} content={'IE=edge'} />
			<meta
				name={'viewport'}
				content={'width=device-width, initial-scale=1'}
			/>
			<meta name={'description'} content={"Yearn web Lib is a library of standard components used through Yearn's Projects. This library is made for React projects with the idea to be light, efficient and easy to use. We are using React + Tailwindcss + ethersjs for the web3 package, and some contexts are available to correctly wrap your app."} />
			<meta name={'msapplication-TileColor'} content={'#62688F'} />
			<meta name={'theme-color'} content={'#ffffff'} />

			<link
				rel={'shortcut icon'}
				type={'image/x-icon'}
				href={'/favicons/favicon.ico'}
			/>
			<link
				rel={'apple-touch-icon'}
				sizes={'180x180'}
				href={'/favicons/apple-touch-icon.png'}
			/>
			<link
				rel={'icon'}
				type={'image/png'}
				sizes={'32x32'}
				href={'/favicons/favicon-32x32.png'}
			/>
			<link
				rel={'icon'}
				type={'image/png'}
				sizes={'16x16'}
				href={'/favicons/favicon-16x16.png'}
			/>
			<link
				rel={'icon'}
				type={'image/png'}
				sizes={'192x192'}
				href={'/favicons/android-chrome-192x192.png'}
			/>
			<link
				rel={'icon'}
				type={'image/png'}
				sizes={'512x512'}
				href={'/favicons/android-chrome-512x512.png'}
			/>

			<meta name={'robots'} content={'index,nofollow'} />
			<meta name={'googlebot'} content={'index,nofollow'} />
			<meta charSet={'utf-8'} />
		</>
	),
	logo: () => {
		// eslint-disable-next-line react-hooks/rules-of-hooks
		return (
			<>
				<div className={'mr-4'}>
					<LogoYearn />
				</div>
				<span
					className={'text-xl font-bold md:inline'}
				>
					{'Yearn Data Analytics'}
				</span>
			</>
		);
	},
	navigation: {next: true, prev: true},
	nextThemes: {defaultTheme: 'light'},
	darkMode: false,
	project: {link: GITHUB_URI},
	unstable_flexsearch: true,
	font: false
};