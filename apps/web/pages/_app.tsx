import {WithYearn} from '@yearn-finance/web-lib/contexts';
import * as React from 'react';
import {ReactElement} from 'react';
import '../style.css';
import {AppProps} from 'next/app';

function	WithLayout(props: AppProps): ReactElement {
	const {Component, pageProps} = props;

	return (
		<div id={'app'} className={'mx-auto mb-0 mt-2 flex max-w-6xl'}>
			<div className={'flex min-h-[100vh] w-full flex-col'}>
				<Component
					router={props.router}
					{...pageProps} />
			</div>
		</div>
	);
}

function	App(props: AppProps): ReactElement {
	const {Component, pageProps} = props;

	return (
		<WithYearn
			options={{
				ui: {
					shouldUseThemes: false
				}
			}}>
			<>
				<WithLayout
					Component={Component}
					pageProps={pageProps}
					router={props.router}
				/>
			</>
		</WithYearn>
	);
}

export default App;
