import React, {ReactElement} from 'react';
import Document, {DocumentContext, DocumentInitialProps, Head, Html, Main, NextScript} from 'next/document';


class MyDocument extends Document {
	static async getInitialProps(ctx: DocumentContext): Promise<DocumentInitialProps> {
		const initialProps = await Document.getInitialProps(ctx);
		return {...initialProps};
	}

	render(): ReactElement {
		return (
			<Html lang={'en'}>
				<Head>
					<link rel={'preconnect'} href={'https://brand.yearn.finance'} crossOrigin={'true'} />
					<link href={'https://brand.yearn.finance/fonts/fonts.css'} rel={'stylesheet'} />
				</Head>
				<body className={'bg-neutral-0 transition-colors duration-150'}>
					<Main />
					<NextScript />
				</body>
			</Html>
		);
	}
}

export default MyDocument;