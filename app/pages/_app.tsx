import {WithYearn} from '@yearn-finance/web-lib/contexts';
import {useClientEffect} from '@yearn-finance/web-lib/hooks';
import {useTheme} from 'next-themes';
import type {AppProps} from 'next/app';
import * as React from 'react';
import '../style.css';

function WrappedApp({Component, router, pageProps}: AppProps): React.ReactElement {
	const {theme} = useTheme();

	useClientEffect((): void => {
		document.body.dataset.theme = theme;
	}, [theme]);

	return (
		<WithYearn
			options={{
				web3: {
					shouldUseWallets: false,
					shouldUseStrictChainMode: false,
					defaultChainID: 1,
					supportedChainID: [1, 250, 42161, 1337, 31337]
				}
			}}
		>
			<React.Fragment>
				<div id={'app'} className={'mx-auto mb-0 grid max-w-6xl grid-cols-12 flex-col gap-x-4 md:flex-row'}>
					<div className={'col-span-12 flex min-h-[100vh] w-full flex-col px-4'}>
						<Component key={router.route} router={router} {...pageProps} />
					</div>
				</div>
			</React.Fragment>
		</WithYearn>
	);
}

function App(props: AppProps): React.ReactElement {
  const getLayout = (props.Component as any).getLayout || ((page: React.ReactElement): React.ReactElement => page) // eslint-disable-line

	return getLayout(<WrappedApp {...props} />);
}

export default App;
